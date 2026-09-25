# 手順：DNBの記録（習慣データ GAS ＋ ショートカット）

書き手：部門責任者（作業者が作り、チェック済み）。依頼票 2026-09-25-1。
**URL・トークンの実値はここに書かない**（公開リポジトリ）。`<UPDATER_URL>` `<UPDATER_TOKEN>` は更新役GASのもの（としやすが持っている）。

## 置いたもの（データ部が作った）
| もの | 場所 |
|---|---|
| フォルダ「データ部」 | ドライブ「だんごカンパニー」直下（ID：`1tkTQt8myt1HLZahU5aBRQOQ-8veawjt-`） |
| スプレッドシート「習慣データ」 | 「データ部」の中（ID：`1BxLuhkWOdBczRrW2gf2GkhHN5c-znUSACOL5lt8ciPs`）。1枚目に DNB の見出しと 9/25 の初回（N=1・45%）。シート名は GAS の setup で「DNB」に変わる |
| ソース `habit_data.gs`・`appsscript.json` | 「GAS更新」フォルダ（正本は Drive。Git には入れない） |

## としやすの手順（1回だけ）
1. **GASを作る（タップ）**
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=create&title=習慣データGAS&name=habit&parentId=1BxLuhkWOdBczRrW2gf2GkhHN5c-znUSACOL5lt8ciPs`
   → 「プロジェクトを作成しました」と、エディタのリンクが出る（習慣データにくっついた GAS になる）
2. **コードを入れる（タップ）**
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=update&target=habit&file=appsscript.json,habit_data.gs`
   → 「コードを反映しました」
3. **setup を実行（エディタ）**：1 のエディタのリンクを開く → 上の関数の選択で `setup` → 実行 → Google の許可画面で許可 → 実行ログに出る **トークン** を控える
4. **デプロイ（エディタ）**：右上「デプロイ → 新しいデプロイ → 種類：ウェブアプリ」。実行するユーザー：自分／アクセスできるユーザー：全員 → デプロイ → **ウェブアプリの URL** を控える
5. **（任意）次から自動で反映されるようにする（タップ2回）**
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=deployments&target=habit` で deploymentId を見る →
   `<UPDATER_URL>?token=<UPDATER_TOKEN>&action=settarget&name=habit&scriptId=<scriptId>&file=appsscript.json,habit_data.gs&deploymentId=<deploymentId>`
6. **ショートカット「DNB記録」を作る（iPhone）**
   1. 「数値を尋ねる」：質問「N（何個前）」
   2. 「数値を尋ねる」：質問「正解率（%）」
   3. 「URLの内容を取得」：URL＝4 のウェブアプリの URL／方法＝POST／本文を要求＝JSON
      - `token`（テキスト）＝3 のトークン
      - `action`（テキスト）＝`dnb`
      - `n`（数値）＝1つ目の「尋ねた数値」
      - `accuracy`（数値）＝2つ目の「尋ねた数値」
   4. 「辞書の値を取得」：キー `message`（3 の結果から）
   5. 「通知を表示」：4 の値
   - ホーム画面に置く。おまけ：オートメーション「App → DNBアプリを閉じたとき → DNB記録を実行」
7. **試す**：適当な値で送る → 「DNBを記録しました」と出て、習慣データの DNB シートに1行増えれば成功。試しの行は、ブラウザで `<ウェブアプリのURL>?token=<トークン>&action=dnb_undo` を開けば消える

## 実際にやった結果（2026-09-25 チャット側ととしやす）
- 1〜8 を終えた。版 `2026-09-25.1`。deploymentId は /exec の URL から読み取って settarget した
- ショートカットは、入力の取り違えを防ぐため「変数を設定」で N・正解率に名前を付けた（5アクション → 7アクション）
- テスト（N=1・50%）→ `dnb_undo` で削除。秘書が習慣データを読み、DNB シートは初回の1行だけと確かめた
- まだ：ホーム画面への追加と、DNB アプリを閉じたときのオートメーション（としやすが設定中）

## 使えること（GAS）
| action | 内容 |
|---|---|
| `ping` | 動作確認（版を返す） |
| `dnb`（`n`, `accuracy`, `memo`） | DNB を1行記録（n=1〜20、正解率=0〜100） |
| `dnb_undo` | DNB の最後の1行を取り消す（押し間違い用） |
| `dnb_last` | DNB の最後の記録を返す |

## 気をつけること
- 「GAS更新」フォルダの `appsscript.json` は、今は習慣データGAS（target=habit）用。ほかのターゲットでマニフェストを反映するときは、ファイル名が重ならないように注意する
- 習慣を増やすときは、`habit_data.gs` の `SHEETS` に1行足し、action を足して、update を1回タップするだけ
