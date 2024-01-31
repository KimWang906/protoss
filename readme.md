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

## 1. SIGSEGV Trigger

### Date: 2024/01/08 ~ 2024/01/12

* 이 트리거는 `User::handle_signin(User *this, const protoss::SignIn *request)` 기능에서 발생한다.

### 발생 위치

```cpp
__int64 __fastcall MySQLClient::exec_query_result(MySQLClient *conn, char *sqlQuery)
{
  __int64 exec_query; // rax

  if ( std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::empty(sqlQuery) )
    exit(-1);
  exec_query = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::c_str(sqlQuery);
  mysql_query(conn, exec_query);
  return mysql_store_result();                  // Get all result
}

User::handle_signin(User *this, const protoss::SignIn *request) {
    /* ... */
      exec_result = MySQLClient::exec_query_result(conn, (char *)data);
      std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::~basic_string((__int64)data);
      if ( exec_result ) /* <-------------- */
      {
        if ( mysql_num_fields(exec_result) == 3 )
        {
          row = mysql_fetch_row(exec_result);
          this->id = atoi(*row);
          std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::operator=(
            this->username,
            row[1]);
          this->amount = atoi(row[3]);
          this->is_login = 1;
          status_code = 0;
        }
      } /* ... */
}
```

위 코드에서 **SIGSEGV**가 발생하는 위치는 `if ( exec_result )` 이후이다.(집 가서 자세히 씁시다)  
발생 원인은 `exec_query_result` 함수 내에서 `mysql_query()`를 사용하게 되는데 해당 함수의 결과가 없음에도 `0(Success)`을 반환한다.  
그렇기에 `mysql_store_result()` 함수도 `mysql_query()`의 결과로 인해 NULL 포인터를 반환하게 되고, NULL 포인터에 접근하는 코드에서 **SIGSEGV**가 발생하였다.  

## Debugging

우선 프로그램 내에 system 함수가 있기에 디버깅 모드를 `set follow-fork-mode parent`로 설정하여 부모 프로세스 중심으로 디버깅이 되도록 설정한다.  

## Program flow

이 프로그램은 코인 거래 관련 프로그램이다.  
기본적으로 protobuf를 통해 데이터를 서버에 전달할 수 있다.  
  
각 기능들의 결과는 다음과 같다:  

* 기본적으로 회원가입 시, `acc_id`는 순차적으로 발급되고 `krw_amount = 100000000;`의 돈을 지급받는다.

* 로그인 시, User 객체에 