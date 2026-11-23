# Rec 字段表

共 226 个当前源码字段。编号和固定 DLL 状态说明见 [字段目录](fields.md)。

按需查找：固定及隐藏字段；Aux 内部辅助通道；ExAux 外部辅助通道。

## 固定及隐藏字段

| 十进制 ID | 当前源码字段名 | 源码中文表头 | 固定 DLL 名称识别 |
|---:|---|---|---|
| 16385 | `Rec.Index` | 记录序号 | 一致 |
| 16386 | `Rec.TestTime` | 测试时间 | 一致 |
| 16387 | `Rec.StepTime` | 步骤时间 | 一致 |
| 16388 | `Rec.Current` | 电流 | 一致 |
| 16389 | `Rec.Capacity` | 容量 | 一致 |
| 16390 | `Rec.SpeCap` | 比容量 | 一致 |
| 16391 | `Rec.SocDod` | SOC\|DOD | 一致 |
| 16392 | `Rec.Voltage` | 电压 | 一致 |
| 16393 | `Rec.Energy` | 能量 | 一致 |
| 16394 | `Rec.SpeEnergy` | 比能量 | 一致 |
| 16395 | `Rec.SysTime` | 系统时间 | 一致 |
| 16399 | `Rec.SysTimeAsLong` | — | 一致 |
| 16400 | `Rec.IncubatorTemp` | 温箱温度 | 一致 |
| 16401 | `Rec.Power` | 功率 | 一致 |
| 16402 | `Rec.SysTimeAsDouble` | — | 一致 |
| 16403 | `Rec.dQdV` | dQ/dV | 一致 |
| 16404 | `Rec.dVdQ` | dV/dQ | 一致 |
| 16405 | `Rec.dSpeQdV` | dSpeQ/dV | 一致 |

## Aux 内部辅助通道

| 名称前缀 | 后缀范围 | 首 ID | 末 ID |
|---|---|---:|---:|
| `Rec.AuxVolt` | 01–64 | 16928 | 16991 |
| `Rec.AuxForce` | 01–16 | 17024 | 17039 |
| `Rec.AuxTemp` | 01–32 | 16896 | 16927 |
| `Rec.AuxPressure` | 01–16 | 17040 | 17055 |

| 十进制 ID | 当前源码字段名 | 源码中文表头 | 固定 DLL 名称识别 |
|---:|---|---|---|
| 16896 | `Rec.AuxTemp01` | 辅温T1 | 一致 |
| 16897 | `Rec.AuxTemp02` | 辅温T2 | 一致 |
| 16898 | `Rec.AuxTemp03` | 辅温T3 | 一致 |
| 16899 | `Rec.AuxTemp04` | 辅温T4 | 一致 |
| 16900 | `Rec.AuxTemp05` | 辅温T5 | 一致 |
| 16901 | `Rec.AuxTemp06` | 辅温T6 | 一致 |
| 16902 | `Rec.AuxTemp07` | 辅温T7 | 一致 |
| 16903 | `Rec.AuxTemp08` | 辅温T8 | 一致 |
| 16904 | `Rec.AuxTemp09` | 辅温T9 | 一致 |
| 16905 | `Rec.AuxTemp10` | 辅温T10 | 一致 |
| 16906 | `Rec.AuxTemp11` | 辅温T11 | 一致 |
| 16907 | `Rec.AuxTemp12` | 辅温T12 | 一致 |
| 16908 | `Rec.AuxTemp13` | 辅温T13 | 一致 |
| 16909 | `Rec.AuxTemp14` | 辅温T14 | 一致 |
| 16910 | `Rec.AuxTemp15` | 辅温T15 | 一致 |
| 16911 | `Rec.AuxTemp16` | 辅温T16 | 一致 |
| 16912 | `Rec.AuxTemp17` | 辅温T17 | 一致 |
| 16913 | `Rec.AuxTemp18` | 辅温T18 | 一致 |
| 16914 | `Rec.AuxTemp19` | 辅温T19 | 一致 |
| 16915 | `Rec.AuxTemp20` | 辅温T20 | 一致 |
| 16916 | `Rec.AuxTemp21` | 辅温T21 | 一致 |
| 16917 | `Rec.AuxTemp22` | 辅温T22 | 一致 |
| 16918 | `Rec.AuxTemp23` | 辅温T23 | 一致 |
| 16919 | `Rec.AuxTemp24` | 辅温T24 | 一致 |
| 16920 | `Rec.AuxTemp25` | 辅温T25 | 一致 |
| 16921 | `Rec.AuxTemp26` | 辅温T26 | 一致 |
| 16922 | `Rec.AuxTemp27` | 辅温T27 | 一致 |
| 16923 | `Rec.AuxTemp28` | 辅温T28 | 一致 |
| 16924 | `Rec.AuxTemp29` | 辅温T29 | 一致 |
| 16925 | `Rec.AuxTemp30` | 辅温T30 | 一致 |
| 16926 | `Rec.AuxTemp31` | 辅温T31 | 一致 |
| 16927 | `Rec.AuxTemp32` | 辅温T32 | 一致 |
| 16928 | `Rec.AuxVolt01` | 辅压U1 | 一致 |
| 16929 | `Rec.AuxVolt02` | 辅压U2 | 一致 |
| 16930 | `Rec.AuxVolt03` | 辅压U3 | 一致 |
| 16931 | `Rec.AuxVolt04` | 辅压U4 | 一致 |
| 16932 | `Rec.AuxVolt05` | 辅压U5 | 一致 |
| 16933 | `Rec.AuxVolt06` | 辅压U6 | 一致 |
| 16934 | `Rec.AuxVolt07` | 辅压U7 | 一致 |
| 16935 | `Rec.AuxVolt08` | 辅压U8 | 一致 |
| 16936 | `Rec.AuxVolt09` | 辅压U9 | 一致 |
| 16937 | `Rec.AuxVolt10` | 辅压U10 | 一致 |
| 16938 | `Rec.AuxVolt11` | 辅压U11 | 一致 |
| 16939 | `Rec.AuxVolt12` | 辅压U12 | 一致 |
| 16940 | `Rec.AuxVolt13` | 辅压U13 | 一致 |
| 16941 | `Rec.AuxVolt14` | 辅压U14 | 一致 |
| 16942 | `Rec.AuxVolt15` | 辅压U15 | 一致 |
| 16943 | `Rec.AuxVolt16` | 辅压U16 | 一致 |
| 16944 | `Rec.AuxVolt17` | 辅压U17 | 一致 |
| 16945 | `Rec.AuxVolt18` | 辅压U18 | 一致 |
| 16946 | `Rec.AuxVolt19` | 辅压U19 | 一致 |
| 16947 | `Rec.AuxVolt20` | 辅压U20 | 一致 |
| 16948 | `Rec.AuxVolt21` | 辅压U21 | 一致 |
| 16949 | `Rec.AuxVolt22` | 辅压U22 | 一致 |
| 16950 | `Rec.AuxVolt23` | 辅压U23 | 一致 |
| 16951 | `Rec.AuxVolt24` | 辅压U24 | 一致 |
| 16952 | `Rec.AuxVolt25` | 辅压U25 | 一致 |
| 16953 | `Rec.AuxVolt26` | 辅压U26 | 一致 |
| 16954 | `Rec.AuxVolt27` | 辅压U27 | 一致 |
| 16955 | `Rec.AuxVolt28` | 辅压U28 | 一致 |
| 16956 | `Rec.AuxVolt29` | 辅压U29 | 一致 |
| 16957 | `Rec.AuxVolt30` | 辅压U30 | 一致 |
| 16958 | `Rec.AuxVolt31` | 辅压U31 | 一致 |
| 16959 | `Rec.AuxVolt32` | 辅压U32 | 一致 |
| 16960 | `Rec.AuxVolt33` | 辅压U33 | 一致 |
| 16961 | `Rec.AuxVolt34` | 辅压U34 | 一致 |
| 16962 | `Rec.AuxVolt35` | 辅压U35 | 一致 |
| 16963 | `Rec.AuxVolt36` | 辅压U36 | 一致 |
| 16964 | `Rec.AuxVolt37` | 辅压U37 | 一致 |
| 16965 | `Rec.AuxVolt38` | 辅压U38 | 一致 |
| 16966 | `Rec.AuxVolt39` | 辅压U39 | 一致 |
| 16967 | `Rec.AuxVolt40` | 辅压U40 | 一致 |
| 16968 | `Rec.AuxVolt41` | 辅压U41 | 一致 |
| 16969 | `Rec.AuxVolt42` | 辅压U42 | 一致 |
| 16970 | `Rec.AuxVolt43` | 辅压U43 | 一致 |
| 16971 | `Rec.AuxVolt44` | 辅压U44 | 一致 |
| 16972 | `Rec.AuxVolt45` | 辅压U45 | 一致 |
| 16973 | `Rec.AuxVolt46` | 辅压U46 | 一致 |
| 16974 | `Rec.AuxVolt47` | 辅压U47 | 一致 |
| 16975 | `Rec.AuxVolt48` | 辅压U48 | 一致 |
| 16976 | `Rec.AuxVolt49` | 辅压U49 | 一致 |
| 16977 | `Rec.AuxVolt50` | 辅压U50 | 一致 |
| 16978 | `Rec.AuxVolt51` | 辅压U51 | 一致 |
| 16979 | `Rec.AuxVolt52` | 辅压U52 | 一致 |
| 16980 | `Rec.AuxVolt53` | 辅压U53 | 一致 |
| 16981 | `Rec.AuxVolt54` | 辅压U54 | 一致 |
| 16982 | `Rec.AuxVolt55` | 辅压U55 | 一致 |
| 16983 | `Rec.AuxVolt56` | 辅压U56 | 一致 |
| 16984 | `Rec.AuxVolt57` | 辅压U57 | 一致 |
| 16985 | `Rec.AuxVolt58` | 辅压U58 | 一致 |
| 16986 | `Rec.AuxVolt59` | 辅压U59 | 一致 |
| 16987 | `Rec.AuxVolt60` | 辅压U60 | 一致 |
| 16988 | `Rec.AuxVolt61` | 辅压U61 | 一致 |
| 16989 | `Rec.AuxVolt62` | 辅压U62 | 一致 |
| 16990 | `Rec.AuxVolt63` | 辅压U63 | 一致 |
| 16991 | `Rec.AuxVolt64` | 辅压U64 | 一致 |
| 17024 | `Rec.AuxForce01` | 压力F1 | 一致 |
| 17025 | `Rec.AuxForce02` | 压力F2 | 一致 |
| 17026 | `Rec.AuxForce03` | 压力F3 | 一致 |
| 17027 | `Rec.AuxForce04` | 压力F4 | 一致 |
| 17028 | `Rec.AuxForce05` | 压力F5 | 一致 |
| 17029 | `Rec.AuxForce06` | 压力F6 | 一致 |
| 17030 | `Rec.AuxForce07` | 压力F7 | 一致 |
| 17031 | `Rec.AuxForce08` | 压力F8 | 一致 |
| 17032 | `Rec.AuxForce09` | 压力F9 | 一致 |
| 17033 | `Rec.AuxForce10` | 压力F10 | 一致 |
| 17034 | `Rec.AuxForce11` | 压力F11 | 一致 |
| 17035 | `Rec.AuxForce12` | 压力F12 | 一致 |
| 17036 | `Rec.AuxForce13` | 压力F13 | 一致 |
| 17037 | `Rec.AuxForce14` | 压力F14 | 一致 |
| 17038 | `Rec.AuxForce15` | 压力F15 | 一致 |
| 17039 | `Rec.AuxForce16` | 压力F16 | 一致 |
| 17040 | `Rec.AuxPressure01` | 液压P1 | 一致 |
| 17041 | `Rec.AuxPressure02` | 液压P2 | 一致 |
| 17042 | `Rec.AuxPressure03` | 液压P3 | 一致 |
| 17043 | `Rec.AuxPressure04` | 液压P4 | 一致 |
| 17044 | `Rec.AuxPressure05` | 液压P5 | 一致 |
| 17045 | `Rec.AuxPressure06` | 液压P6 | 一致 |
| 17046 | `Rec.AuxPressure07` | 液压P7 | 一致 |
| 17047 | `Rec.AuxPressure08` | 液压P8 | 一致 |
| 17048 | `Rec.AuxPressure09` | 液压P9 | 一致 |
| 17049 | `Rec.AuxPressure10` | 液压P10 | 一致 |
| 17050 | `Rec.AuxPressure11` | 液压P11 | 一致 |
| 17051 | `Rec.AuxPressure12` | 液压P12 | 一致 |
| 17052 | `Rec.AuxPressure13` | 液压P13 | 一致 |
| 17053 | `Rec.AuxPressure14` | 液压P14 | 一致 |
| 17054 | `Rec.AuxPressure15` | 液压P15 | 一致 |
| 17055 | `Rec.AuxPressure16` | 液压P16 | 一致 |

## ExAux 外部辅助通道

| 名称前缀 | 后缀范围 | 首 ID | 末 ID |
|---|---|---:|---:|
| `Rec.ExAuxVolt` | 01–16 | 17408 | 17423 |
| `Rec.ExAuxForce` | 01–16 | 17456 | 17471 |
| `Rec.ExAuxTemp` | 01–16 | 17424 | 17439 |
| `Rec.ExAuxPressure` | 01–16 | 17472 | 17487 |
| `Rec.ExAuxThickness` | 01–16 | 17440 | 17455 |

| 十进制 ID | 当前源码字段名 | 源码中文表头 | 固定 DLL 名称识别 |
|---:|---|---|---|
| 17408 | `Rec.ExAuxVolt01` | 辅压Ux1 | 一致 |
| 17409 | `Rec.ExAuxVolt02` | 辅压Ux2 | 一致 |
| 17410 | `Rec.ExAuxVolt03` | 辅压Ux3 | 一致 |
| 17411 | `Rec.ExAuxVolt04` | 辅压Ux4 | 一致 |
| 17412 | `Rec.ExAuxVolt05` | 辅压Ux5 | 一致 |
| 17413 | `Rec.ExAuxVolt06` | 辅压Ux6 | 一致 |
| 17414 | `Rec.ExAuxVolt07` | 辅压Ux7 | 一致 |
| 17415 | `Rec.ExAuxVolt08` | 辅压Ux8 | 一致 |
| 17416 | `Rec.ExAuxVolt09` | 辅压Ux9 | 一致 |
| 17417 | `Rec.ExAuxVolt10` | 辅压Ux10 | 一致 |
| 17418 | `Rec.ExAuxVolt11` | 辅压Ux11 | 一致 |
| 17419 | `Rec.ExAuxVolt12` | 辅压Ux12 | 一致 |
| 17420 | `Rec.ExAuxVolt13` | 辅压Ux13 | 一致 |
| 17421 | `Rec.ExAuxVolt14` | 辅压Ux14 | 一致 |
| 17422 | `Rec.ExAuxVolt15` | 辅压Ux15 | 一致 |
| 17423 | `Rec.ExAuxVolt16` | 辅压Ux16 | 一致 |
| 17424 | `Rec.ExAuxTemp01` | 辅温Tx1 | 一致 |
| 17425 | `Rec.ExAuxTemp02` | 辅温Tx2 | 一致 |
| 17426 | `Rec.ExAuxTemp03` | 辅温Tx3 | 一致 |
| 17427 | `Rec.ExAuxTemp04` | 辅温Tx4 | 一致 |
| 17428 | `Rec.ExAuxTemp05` | 辅温Tx5 | 一致 |
| 17429 | `Rec.ExAuxTemp06` | 辅温Tx6 | 一致 |
| 17430 | `Rec.ExAuxTemp07` | 辅温Tx7 | 一致 |
| 17431 | `Rec.ExAuxTemp08` | 辅温Tx8 | 一致 |
| 17432 | `Rec.ExAuxTemp09` | 辅温Tx9 | 一致 |
| 17433 | `Rec.ExAuxTemp10` | 辅温Tx10 | 一致 |
| 17434 | `Rec.ExAuxTemp11` | 辅温Tx11 | 一致 |
| 17435 | `Rec.ExAuxTemp12` | 辅温Tx12 | 一致 |
| 17436 | `Rec.ExAuxTemp13` | 辅温Tx13 | 一致 |
| 17437 | `Rec.ExAuxTemp14` | 辅温Tx14 | 一致 |
| 17438 | `Rec.ExAuxTemp15` | 辅温Tx15 | 一致 |
| 17439 | `Rec.ExAuxTemp16` | 辅温Tx16 | 一致 |
| 17440 | `Rec.ExAuxThickness01` | 厚度Thx1 | 一致 |
| 17441 | `Rec.ExAuxThickness02` | 厚度Thx2 | 一致 |
| 17442 | `Rec.ExAuxThickness03` | 厚度Thx3 | 一致 |
| 17443 | `Rec.ExAuxThickness04` | 厚度Thx4 | 一致 |
| 17444 | `Rec.ExAuxThickness05` | 厚度Thx5 | 一致 |
| 17445 | `Rec.ExAuxThickness06` | 厚度Thx6 | 一致 |
| 17446 | `Rec.ExAuxThickness07` | 厚度Thx7 | 一致 |
| 17447 | `Rec.ExAuxThickness08` | 厚度Thx8 | 一致 |
| 17448 | `Rec.ExAuxThickness09` | 厚度Thx9 | 一致 |
| 17449 | `Rec.ExAuxThickness10` | 厚度Thx10 | 一致 |
| 17450 | `Rec.ExAuxThickness11` | 厚度Thx11 | 一致 |
| 17451 | `Rec.ExAuxThickness12` | 厚度Thx12 | 一致 |
| 17452 | `Rec.ExAuxThickness13` | 厚度Thx13 | 一致 |
| 17453 | `Rec.ExAuxThickness14` | 厚度Thx14 | 一致 |
| 17454 | `Rec.ExAuxThickness15` | 厚度Thx15 | 一致 |
| 17455 | `Rec.ExAuxThickness16` | 厚度Thx16 | 一致 |
| 17456 | `Rec.ExAuxForce01` | 压力Fx1 | 一致 |
| 17457 | `Rec.ExAuxForce02` | 压力Fx2 | 一致 |
| 17458 | `Rec.ExAuxForce03` | 压力Fx3 | 一致 |
| 17459 | `Rec.ExAuxForce04` | 压力Fx4 | 一致 |
| 17460 | `Rec.ExAuxForce05` | 压力Fx5 | 一致 |
| 17461 | `Rec.ExAuxForce06` | 压力Fx6 | 一致 |
| 17462 | `Rec.ExAuxForce07` | 压力Fx7 | 一致 |
| 17463 | `Rec.ExAuxForce08` | 压力Fx8 | 一致 |
| 17464 | `Rec.ExAuxForce09` | 压力Fx9 | 一致 |
| 17465 | `Rec.ExAuxForce10` | 压力Fx10 | 一致 |
| 17466 | `Rec.ExAuxForce11` | 压力Fx11 | 一致 |
| 17467 | `Rec.ExAuxForce12` | 压力Fx12 | 一致 |
| 17468 | `Rec.ExAuxForce13` | 压力Fx13 | 一致 |
| 17469 | `Rec.ExAuxForce14` | 压力Fx14 | 一致 |
| 17470 | `Rec.ExAuxForce15` | 压力Fx15 | 一致 |
| 17471 | `Rec.ExAuxForce16` | 压力Fx16 | 一致 |
| 17472 | `Rec.ExAuxPressure01` | 液压Px1 | 一致 |
| 17473 | `Rec.ExAuxPressure02` | 液压Px2 | 一致 |
| 17474 | `Rec.ExAuxPressure03` | 液压Px3 | 一致 |
| 17475 | `Rec.ExAuxPressure04` | 液压Px4 | 一致 |
| 17476 | `Rec.ExAuxPressure05` | 液压Px5 | 一致 |
| 17477 | `Rec.ExAuxPressure06` | 液压Px6 | 一致 |
| 17478 | `Rec.ExAuxPressure07` | 液压Px7 | 一致 |
| 17479 | `Rec.ExAuxPressure08` | 液压Px8 | 一致 |
| 17480 | `Rec.ExAuxPressure09` | 液压Px9 | 一致 |
| 17481 | `Rec.ExAuxPressure10` | 液压Px10 | 一致 |
| 17482 | `Rec.ExAuxPressure11` | 液压Px11 | 一致 |
| 17483 | `Rec.ExAuxPressure12` | 液压Px12 | 一致 |
| 17484 | `Rec.ExAuxPressure13` | 液压Px13 | 一致 |
| 17485 | `Rec.ExAuxPressure14` | 液压Px14 | 一致 |
| 17486 | `Rec.ExAuxPressure15` | 液压Px15 | 一致 |
| 17487 | `Rec.ExAuxPressure16` | 液压Px16 | 一致 |
