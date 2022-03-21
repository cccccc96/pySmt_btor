# 实现任务

## ToPySmt 语法

Memory中应支持语法

基本类型
- [x] bitvec sort
- [x] bitvec const
- [x] array sort
- [x] ~~array const~~ memory里好像没这东西，不过我也写了
- [x] symbol

操作符

- [x] not
- [x] and
- [x] concat
- [x] redor
- [x] or
- [x] eq
- [x] ite
- [x] ult
- [x] write
- [x] read

idx操作符
- [x] uext

转移关系
- [x] init
- [x] next

属性
- [x] constrain
- [x] output
- [x] bad

### ps:
之前bitvec类型把长度为1的时候设置成BOOL类型，感觉有点不太对，现在还是改成正常当作BVType(1)处理

### 待解决的问题
主要还是pySmt怎么去设计
* btor2里只有bitvec和array两类。pySmt也提供了对于bitvec的各种函数，但是这些函数的返回值不全是BV类型，有些函数返回BOOL类型，这在btor2里是没有的，这就有问题了（一个一个门往后加的时候有可能变成BOOL和bitvec做运算，就报错了）。
* 再去查点pySmt的教程，或者去pono或者boolector里看看那些parser是咋弄的。