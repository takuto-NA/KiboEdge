# KiboEdge Tool Call Kit

LM Studio (`http://127.0.0.1:1234/v1`) + `lfm2-2.6b-exp` 向けの、ツールコール安定化ライブラリです。  
目的は、**厳密成功率**（tool名/argumentsがschema一致して1回で実行可能）を段階的に改善することです。

## What this repository provides

- 逐次実行固定の `ToolCallEngine`（並列実行しない）
- `tool_calls` 優先 + content方言フォールバック parser
- 30ケース評価データセットと厳密成功率評価ランナー
- プロンプト改善ループ用スクリプト
- 効果音/カレンダー/TODO/天気/ニュース/DB読書きのダミーツール

## Safety defaults (for unstable local PCs)

- 1回の評価はデフォルト `1` ケース
- 1ケースごとに待機（クールダウン）あり
- 連続 request error で早期停止
- APIタイムアウトは短め（12秒）

## Install

```bash
python -m pip install -e .
```

## Quick smoke test

```bash
set PYTHONPATH=src
python scripts/run_smoke_tests.py
```

## Run strict-success evaluation

```bash
set PYTHONPATH=src
python scripts/run_evaluation.py --max-cases 1 --request-timeout-seconds 12
```

結果は `logs/evaluations/` に JSON 保存されます。

## Run improvement iteration (prompt variants)

```bash
set PYTHONPATH=src
python scripts/run_iteration_and_improve.py --max-cases 1 --request-timeout-seconds 12
```

baseline prompt と strict-json prompt を逐次で比較します。

## Library usage

```python
from kiboedge_toolcall_kit import (
    RuntimeConfiguration,
    ToolCallEngine,
    build_tool_schemas,
    DummyDataStores,
    build_tool_executor_map,
)
from kiboedge_toolcall_kit.lmstudio_client import LmStudioChatClient
from kiboedge_toolcall_kit.lfm_tool_call_parser import LfmToolCallParser

runtime_configuration = RuntimeConfiguration()
tool_call_engine = ToolCallEngine(
    runtime_configuration=runtime_configuration,
    chat_client=LmStudioChatClient(runtime_configuration),
    tool_schemas=build_tool_schemas(),
    tool_executor_map=build_tool_executor_map(DummyDataStores()),
    parser=LfmToolCallParser(),
)
result = tool_call_engine.run_tool_call_round("東京の明日の天気を教えて")
print(result)
```

## Structure

- `src/kiboedge_toolcall_kit/config.py`: 設定値一元化
- `src/kiboedge_toolcall_kit/tool_orchestrator.py`: 逐次ツール実行エンジン
- `src/kiboedge_toolcall_kit/lfm_tool_call_parser.py`: LFM方言フォールバック parser
- `src/kiboedge_toolcall_kit/evaluation_runner.py`: 評価実行
- `src/kiboedge_toolcall_kit/evaluation_metrics.py`: 成功率・失敗理由集計
- `tests/fixtures/tool_call_cases_30.json`: 30ケース定義

## Notes

- 並列API呼び出しは実装していません（PC保護のため）。
- 実データ連携ではなく全てダミー実装です。
- LM Studio側でモデルをロード済みであることを前提にしています。
