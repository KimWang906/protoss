# Build

See Dockerfile

## Protobuf C++ Generated Code Guide

* [Reference](https://protobuf.dev/reference/cpp/cpp-generated/)

## Protoss Reversing

* Restore [protoss.proto](proto/protoss.proto)
* [ProtoBuf Techniques](https://protobuf.dev/programming-guides/techniques/)

우선 protoss에서 사용하는 proto 파일을 복원하는 작업을 해보았음.
여기서 중요한 건 proto 버전인데 이 버전에 따라서 문법에서 강제되는 요소(각 필드마다 optoinal, required 등을 기입해야함)가 있음.

그러나 protoss(baby, adult) 바이너리에서는 이 버전을 유추할만한 요소가 있는데
각 Class에 있는 IsInitialized의 구현을 확인하면 된다.

proto 버전 3부터는 optional과 required를 강제하는 문법이 사라져 아래와 같은 구현이 되어 있다.

```cpp
_BOOL8 __fastcall protoss::Sell::IsInitialized(protoss::Sell *this)
{
  return 1;
}
```

그러나 proto 버전 2의 IsInitialized는 required를 검사하는 API가 존재한다.

```cpp
_BOOL8 __fastcall protoss::Sell::IsInitialized(protoss::Sell *this)
{
  return (unsigned __int8)protoss::Sell::_Internal::MissingRequiredFields((char *)this + 16) == 0;
}

bool __fastcall protoss::Sell::_Internal::MissingRequiredFields(_DWORD *a1)
{
  return (~(unsigned __int8)*a1 & 5) != 0;
}
```

위 코드는 Bit Field 연산을 통해 required의 여부를 검사한다. 또한 이 코드로 proto2에서 required의 갯수를 알 수 있다. required의 필드 위치도 알 수 있는 것 같은데 확실하지 않음.
변환된 proto c++ 코드 보고 protoss 바이너리 비교하면서 확인할 것.

## Find Vulnability

SIGSEGV 발생 --> 1 -> 2 -> HyunBin / 12345678로 회원가입 -> 1 -> 3 -> HyunBin / 12 --> SIGSEGV

확인 결과 login_count가 set되지 않았을 때, SIGSEGV를 발생시킬 수 있음.
--> 최초 로그인 시 비밀번호를 의도적으로 틀리게 하여 발생시킬 수 있다.
--> 만약 로그인에 성공했을 경우, 이후 로그인은 다중 로그인 시도로 감지되어 실패함.
