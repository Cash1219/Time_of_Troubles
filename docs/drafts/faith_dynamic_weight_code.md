# 信仰动态消费：候选代码与验证步骤

这份文档不参与游戏加载。第一步的常数引用测试已写入模组；后续条件写法仍是候选代码，尚未经过游戏运行验证。

当前faith本地商品设定已实装；需求条目的weight引用tot_faith_need_weight，该脚本值固定返回0.8。本方案不新增需求组、不改变服务组消费包、不调整PM产出。

## 第一步：只测试字段能否引用脚本值

已在 `common/script_values/tot_faith_consumption_values.txt` 添加：

```text
tot_faith_need_weight = 0.8
```

将现有服务需求中faith条目的weight替换为该名称，其余条目保留：

```text
entry = {
    goods = faith
    weight = tot_faith_need_weight
    max_supply_share = 0.4
    min_supply_share = 0.0
}
```

该代码片段须放在现有popneed_services内，不能作为独立entry顶层文件。先检查加载日志是否接受脚本值名称；再改变测试值确认实际使用该值。仅加载不报错不能证明动态求值。

测试状态：静态检查可确认定义和引用对应，但尚未完成游戏加载测试。需完全退出并重启游戏，检查error.log中与tot_faith_need_weight、pop_needs有关的错误，并确认人口消费界面仍有信仰需求。随后以同一存档、相同供给条件对比0.8与较明显的测试值，验证权重确实参与消费计算；测试后恢复0.8。若字段不接受名称，直接将faith条目的weight恢复为0.8，并移除本测试脚本值文件。

## 第二步：测试法律与人口作用域

下文**假设调用时作用域为pop**。在该假设下，owner为国家、state为本州。这些作用域路径在原版人口脚本中存在，但尚未确认需求字段会以pop作为调用上下文。若引擎不提供这一上下文，本写法即不成立。

第一轮测试只写法律部分，不加教士项。验证同一市场中两国人口能否得到不同权重、变更法律后是否更新。需要区分在数据库加载时读取一次和随消费动态读取。

通过后，完整候选脚本值为：

```text
tot_faith_need_weight = {
    value = 0.8

    if = {
        limit = { owner = { has_law_or_variant = law_type:law_state_atheism } }
        multiply = 0.1
    }
    else_if = {
        limit = { owner = { has_law_or_variant = law_type:law_state_religion } }
        multiply = 2
    }
    else_if = {
        limit = { owner = { has_law_or_variant = law_type:law_freedom_of_conscience } }
        multiply = 1.25
    }
    # Total separation and other unmatched laws retain factor 1.

    multiply = tot_faith_clergy_factor
}

tot_faith_clergy_factor = {
    value = 0.8

    if = {
        limit = {
            state = {
                pop_type_percent_state = {
                    target = pop_type:clergymen
                    value >= 0.02
                }
            }
        }
        value = 1.2
    }
    else_if = {
        limit = {
            state = {
                pop_type_percent_state = {
                    target = pop_type:clergymen
                    value >= 0.015
                }
            }
        }
        value = 1.1
    }
    else_if = {
        limit = {
            state = {
                pop_type_percent_state = {
                    target = pop_type:clergymen
                    value >= 0.01
                }
            }
        }
        value = 1
    }
    else_if = {
        limit = {
            state = {
                pop_type_percent_state = {
                    target = pop_type:clergymen
                    value >= 0.005
                }
            }
        }
        value = 0.9
    }
}
```

教士占比阈值沿用讨论草案，并未用开局分布校准。使用原版state职业占比判定，避免按每个消费人口遍历整州全部pop；只返回0.8—1.2的小幅调整。是否需要缓存按实际运行性能决定，不先添加月度事件循环。

## 第三步：无神论人口的商品禁忌

在已有atheist宗教块中增加下列字段，而不是重写整份religion文件：

```text
taboos = { faith }
```

采用原版全局禁忌需求倍率0.5，不改全局define。这个机制按人口宗教生效，与国家法律系数分开。其实际消费效果不得简单说成最终订单固定再减半。

## 通过条件与失败处理

1. weight接受脚本引用且采用返回值。
2. 运行时能从需求调用上下文取到对应人口的国家与州。
3. 法律变更与教士占比跨阈值后，实际权重更新。
4. 修改只影响faith替代选择，未改变整组预算、其他国家的人口文化或全局禁忌。
5. 检查普通服务与体验能继续承接消费，无faith供应不产生必须购买faith的单商品消费组。

任一动态前提失败，就不把该脚本接入正常模组。保留当前固定权重和本地商品设定，另评估人口宗教禁忌或其他已确认机制。统计教士与缓存变量本身不能绕过需求字段缺少动态求值的问题。
