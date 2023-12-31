#  Build

```

```

# Protobuf C++ Generated Code Guide

* [Reference](https://protobuf.dev/reference/cpp/cpp-generated/)

# Protoss Reversing

```proto
syntax = "proto2";

// Reverse Engineering
// proto ver: 2

package protoss;

message SignUp {
    required string username = 1;
    required string password = 2;
}

message SignUpResponse {
    required string username = 1;
    required string password = 2;
}

message SignIn {
    required string username = 1;
    required string password = 2;
}

message Buy {
    required uint64 symbol = 1;
    required uint64 amount = 2;
    optional uint64 timestamp = 3;
}

message TradeResponse {
    required string symbol = 1;
    required uint64 coin_cur_price = 2;
    required uint64 amount = 3;
    required uint64 total_price = 4;
    required bool flag = 5;
}

message Sell {
    required uint64 amount = 1;
    optional uint64 timestamp = 2;
    required uint32 symbol = 3;
}

message History {
    required uint64 type = 1;
    optional uint64 timestamp = 2;
    required uint32 symbol = 3;
}

message HistoryResponse {
    required uint64 id = 1;
    required uint64 price = 2;
    required uint64 amount = 3;
    required uint64 total_price = 4;
    required uint64 trade_time = 5;
    required bool type = 6;
}

message AddressBook {
    required string address = 1;
    optional string memo = 2;
    optional uint64 create_at_timestamp = 3;
    required uint32 symbol = 4;
}

message AddressBookResponse {
    required string symbol = 1;
    required string address = 2;
    optional string memo = 3;
}

message ModifyAddressBook {
    required string origin_addr = 1;
    required string new_addr = 2;
    required uint32 id = 3;
}

message ModifyAddressBookResponse {
    required string origin_addr = 1;
    required string new_addr = 2;
    required uint32 id = 3;
}

message Deposit {
    required string address = 1;
    optional uint64 memo = 2;
    required uint32 symbol = 3;
}

message ProtossInterface {
    optional SignUp event_signup = 1;
    optional SignIn event_signin = 2;
    optional Deposit event_deposit = 3;
    optional Buy event_buy = 4;
    optional Sell event_sell = 5;
    optional History event_history = 6;
    optional AddressBook event_addressbook = 7;
    optional ModifyAddressBook event_modify_addressbook = 8;
    required uint32 event_id = 9;
}
```

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