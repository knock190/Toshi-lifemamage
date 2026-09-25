# 役目書：データ部

書き手：部門責任者（役目の変更はとしやすが決める）。部門の決まりは `company/rules.md` 8-8。

| 項目 | 内容 |
|---|---|
| 部門名 | データ部 |
| 何のため | 事業を支える。習慣のデータを集めて、見える・使える形にする |
| 役目 | 1. **データを貯める**：スプレッドシート「習慣データ」と、その GAS の管理<br>2. **貯め方・仕組みを考える**：新しい習慣が来たら、シートと入力の方法を作る（としやすの手間は最小に）<br>3. **一目で見られるようにする**：グラフのページ（毎朝 5:00 に秘書が更新）<br>4. **事業をまたいで使う**：データから分かったことを、Ωに提案する |
| 良し悪しの見方 | 頼まれたことに応えられたか／データの抜けがないか／グラフが毎朝更新されているか／提案が使われたか |
| 開始 | 2026-09-25 |
| 状態 | 立ち上げ |

## 決まっていること（2026-09-25 としやす決定。`company/decisions.md`）
- 習慣のデータは、1つのスプレッドシート「習慣データ」にシート（DNB・体重・筋トレ…）で分けて貯める。Git には貯めない
- 入力は iPhone ショートカット → GAS → スプレッドシート（DNB）。GAS はチャットから作る仕組み（`company/gas-remote-update.md`）で作る
- グラフは claude.ai のWebページで、毎朝 5:00 に秘書がデータを入れ直す
- サプリ管理DBは今動いているので、すぐには移さない（読むだけ）
- **このリポジトリは公開。ウェブアプリの URL・トークンの実値は絶対に書かない**

## 置き場所
- ドライブ「だんごカンパニー/データ部」（ID：`1tkTQt8myt1HLZahU5aBRQOQ-8veawjt-`）
- スプレッドシート「習慣データ」（ID：`1BxLuhkWOdBczRrW2gf2GkhHN5c-znUSACOL5lt8ciPs`）。シート：DNB
- GAS：習慣データにくっついた「習慣データGAS」（更新役の target=habit。scriptId：`1DNFJuS5wk8WvNVaimOuRDfwKMtPn813f60JMmn7XcMGNLqcJqkGN6ywM`。deploymentId 登録済みで、Drive のソースを直して update すれば /exec まで反映される。2026-09-25 稼働）。ソースは「GAS更新」フォルダの `habit_data.gs`・`appsscript.json`
- 手順：`setup-dnb.md`
- グラフのページ「だんご習慣ボード」：https://claude.ai/artifact/NvqkZHYzHPn426kjSxkaye （非公開。型は `board.html`、データの入れ方は下）

## 毎朝のボードの更新（秘書が 5:00 の回でやる）
1. 「習慣データ」の DNB シートと「サプリ管理DB」の master・log シートを読む
2. `board.html` の `board-data` と同じ形の JSON を **スクラッチ（Git の外）** に作る（updated＝今の日本時間、dnb.rows＝DNB の全行、supp.log＝log の日時の全部、weeklyTarget＝master の週の目標回数）
3. `python3 departments/data/build_board.py <JSON> <スクラッチ>/habit-board.html`
4. Artifact ツールで、その HTML を `url`＝上のリンクにして公開する（同じリンクのまま更新される）
- データは Git に入れない。`board.html`（型）を直すのはデータ部

## 数字の意味は事業が見る
データ部は仕組みと見せ方を持つ。数字の意味（DNBの伸び・サプリの達成など）を判断するのは、その事業。
