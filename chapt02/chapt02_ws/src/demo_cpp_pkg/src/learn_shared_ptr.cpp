#include <iostream>
#include <memory>
using namespace std;

int main(){
  auto sp1 = make_shared<string>("this is a ptr");   //make_shared<数据类型/类名>(数据值/构造函数参数)>
  cout<<"sp1: "<<*sp1<<endl;
  auto sp2 = sp1;
  cout<<"sp2: "<<*sp2<<endl;
  *sp2 = "this is a new value";
  cout<<"sp1: "<<*sp1<<endl;
  cout<<"sp2: "<<*sp2<<endl;
  return 0;
}


