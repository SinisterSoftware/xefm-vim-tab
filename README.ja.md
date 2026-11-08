# Vim Terminal Tab

XeFM からローカルのテキストファイルを、Windows Terminal の Vim で開く拡張機能です。すでに Vim のサーバーが動いていれば、その Vim に新しいタブを追加します。動いていなければ Windows Terminal にタブを作って Vim を起動します。

[English](README.md)

## 必要な環境

- Windows と XeFM 1.10.0 以降。拡張機能の API バージョンは 1 です。
- `vim`、Windows Terminal の `wt`、Windows PowerShell の `powershell` が XeFM の実行環境の `PATH` から見つかること。
- 既存の Vim にファイルを追加するには、`+clientserver` に対応した Vim が必要です。`vim --version` の出力で `+clientserver` を確認してください。

例として PowerShell で次のように確認できます。

```powershell
Get-Command xefm, vim, wt, powershell
vim --version | Select-String clientserver
```

XeFM を起動した後に `PATH` を変更した場合は、XeFM を再起動して新しい環境変数を反映してください。

## インストール

PowerShell などで実行します。

```powershell
xefm ext check github:SinisterSoftware/xefm-vim-tab
xefm ext install github:SinisterSoftware/xefm-vim-tab
```

インストール時に表示される追加内容を確認して進めてください。完了後、XeFM の **Tools ▸ Reload Configuration** を実行するか、XeFM を再起動します。`xefm ext list` でインストール状態を確認できます。

バージョン指定のない GitHub ソースは、通常、最新のリリースタグをインストールします。リポジトリの `main` にある変更が、まだリリースタグに含まれていないこともあります。特定のタグを指定する場合は、例えば `github:SinisterSoftware/xefm-vim-tab@v0.1.1` を使用します。

## 使い方

1. XeFM のファイル一覧で、開きたいローカルファイルにカーソルを合わせます。
2. **File** メニューまたはファイルのコンテキストメニューから **Edit in Vim tab** を選びます。コマンドパレットで `vim-tab.edit-file` を検索して実行することもできます。
3. Vim で編集し、通常どおり `:w` で保存、`:q` で終了します。複数ファイルを開いたときは Vim の `:tabnext`、`:tabprevious` などで Vim 内のタブを切り替えられます。

対象は**選択済みの複数ファイルではなく、カーソル下の項目**です。メニュー項目はカーソル下に項目があるときに使用できます。

拡張機能は `E` をショートカット候補として提示しますが、すでに使われているキーには自動適用されません。使用中のキーマップや設定によって結果は変わります。`xefm keys E vim-tab.edit-file edit_file` で確認してください。

この拡張機能は `vim-tab.edit-file` という**別のアクション**を登録します。XeFM 標準の `edit_file` やその `E` / `F4` を必ず置き換えるわけではありません。拡張機能のアクションを呼び出すには、メニュー、コマンドパレット、または割り当てたキーを使用してください。

### キーの割り当て例

`~/.xefm/config.py`（Windows では通常 `%USERPROFILE%\.xefm\config.py`）の `class Config:` に、たとえば次の設定を追加します。

```python
class Config:
    KEY_BINDINGS = {
        'vim-tab.edit-file': ['Ctrl-Shift-E'],
    }
```

既存の `Config` や `KEY_BINDINGS` がある場合は作り直さず、既存の辞書に `'vim-tab.edit-file'` の行を追加してください。例のキーも含め、他のアクションとの競合を `xefm keys Ctrl-Shift-E` で確認してください。同じキーを複数のアクションに割り当てると、片方が実行されないことがあります。保存後、**Tools ▸ Reload Configuration** を実行するか再起動します。

たとえば標準の編集キーを `F4` から移したい場合は、既存の `KEY_BINDINGS` に次を追加できます。

```python
    KEY_BINDINGS = {
        'edit_file': [],
        'vim-tab.edit-file': ['F4'],
    }
```

`edit_file: []` は標準の編集アクションに割り当てられたキーをすべて外します。標準の編集操作もキーで使いたい場合は、空リストの代わりに競合しない別のキーを指定してください。設定後、`xefm keys F4 edit_file vim-tab.edit-file` で確認できます。

## 動作と制約

- このアクションは、カーソル下の項目がファイルで、ローカルのパスを読み取れる場合に限り Vim で開こうとします。`://` を含むパスなどの仮想ファイル、ディレクトリ、読み取れないファイルは Vim に直接渡さず、XeFM 標準の `edit_file` に処理を渡します。標準アクションで開けるかどうかは XeFM 側の設定や対象によります。
- テキストかどうかは、ファイルの**先頭 8192 バイトに NUL バイトがないか**で簡易判定します。拡張子や文字コードは判定しません。NUL を含む UTF-16 などのテキストが対象外になったり、NUL のないバイナリがテキストと判定されたりします。空ファイルはテキストと判定されます。
- `vim --serverlist` に `XEFM` というサーバーがあれば、`--remote-tab-silent` でその Vim にファイルを渡します。なければ `wt -w 0 new-tab` で Windows Terminal にタブを作成し、`vim --servername XEFM` を起動します。
- 新しい Windows Terminal タブのタイトルは `XEFM-VIM` です。既存の Vim を再利用するときは、PowerShell と Windows UI Automation を使って同名のターミナルタブへの切り替えを試みます。切り替えが失敗してもファイルを開く処理は続行します。
- `XEFM` というサーバー名や `XEFM-VIM` というタブ名は固定です。同じ名前の別の Vim サーバーやタブがあると、意図しないものが対象になる可能性があります。拡張機能固有の設定項目はありません。
- 起動時などに Python 側で例外が起きた場合は `vim 起動失敗: ...` を表示し、標準の `edit_file` に処理を渡します。一方、外部コマンドの終了コードや UI Automation によるフォーカス成功は確認していないため、エラーメッセージがなくてもファイルやタブが期待どおり開かない場合があります。

## よくある問題

**メニューやキーが表示・動作しない**

`xefm ext list` で有効状態を確認し、設定を再読み込みするか XeFM を再起動してください。`E` は候補であり、既存の割り当てと競合すると使えないことがあります。`xefm keys E vim-tab.edit-file edit_file` と、必要に応じて使用中のキーを確認してください。メニューやコマンドパレットからも実行できます。

**必要なプログラムが見つからない**

上記の `Get-Command` で `vim`、`wt`、`powershell` を確認し、XeFM から参照できる `PATH` に追加して XeFM を再起動してください。拡張機能はこれらを必須プログラムとして宣言しており、不足するとアクションを実行できません。

**毎回新しい Windows Terminal タブが開く、または既存の Vim に追加されない**

`vim --version` で `+clientserver` を確認し、`vim --serverlist` に `XEFM` が表示されるか確認してください。別名の Vim サーバーは再利用対象ではありません。Vim の終了後は新たに起動します。

**ファイルは開いたがターミナルタブに切り替わらない**

Windows Terminal の `XEFM-VIM` タブを手動で選択してください。UI Automation による切り替えは環境によって失敗することがあります。

**一部のファイルが標準エディターで開く**

仮想パス、読み取れないファイル、先頭 8192 バイトに NUL があるファイルなどは標準の `edit_file` に渡されます。これは拡張機能の簡易判定による動作です。

## 更新・無効化・削除

```powershell
xefm ext outdated
xefm ext upgrade vim-tab
xefm ext disable vim-tab
xefm ext enable vim-tab
xefm ext uninstall vim-tab
```

更新は公開済みタグを参照します。変更後は XeFM の **Tools ▸ Reload Configuration** を実行するか、再起動してください。削除後に `config.py` に残る `vim-tab.edit-file` のキー設定は不要であれば削除してください。

## 開発

リポジトリのディレクトリで、拡張機能の静的な検査とテストを実行できます。

```powershell
xefm ext check .
python -m pytest tests
```

ライセンスは [MIT License](LICENSE) です。
