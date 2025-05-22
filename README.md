# PokeAPI MCP Server

This project implements a Model Context Protocol (MCP) server using FastMCP. The server interacts with the [PokeAPI](https://pokeapi.co/) to provide tools for querying Pokémon and item information. This server is designed to be easily consumable by AI Agents.


![image](https://github.com/user-attachments/assets/de44438c-66f6-4057-bff2-5e1646a4676c)
![image](https://github.com/user-attachments/assets/d90cb181-4a5d-4f40-ad0a-1572ef4fbf8c)


## Features

The server exposes the following tools:

*   `get_pokemon_details(pokemon_name_or_id: str)`: Fetches comprehensive details for a specific Pokémon.
*   `get_pokemon_types(pokemon_name_or_id: str)`: Fetches the elemental types of a specific Pokémon.
*   `get_pokemon_color(pokemon_name_or_id: str)`: Fetches the Pokedex color of a specific Pokémon.
*   `get_pokemon_shape(pokemon_name_or_id: str)`: Fetches the Pokedex shape category of a specific Pokémon.
*   `list_all_pokemon_names(limit: int = 2000, offset: int = 0)`: Lists English names of Pokémon, supporting pagination.
*   `get_item_details(item_name_or_id: str)`: Fetches detailed information about a specific in-game item.
*   `list_all_items(limit: int = 100, offset: int = 0)`: Lists in-game items, supporting pagination.

Refer to the `SERVER_INSTRUCTIONS` variable and individual tool docstrings in `server.py` for more detailed information on each tool's parameters and return values.

## Setup

1.  **Prerequisites:**
    *   Python  (Python 3.10 or newer recommended for `httpx` async features)
    *   `uv` (Recommended: an extremely fast Python package installer and resolver. )
    *   Alternatively, `pip` and `virtualenv` (or `venv` if not using `uv`)

2.  **Create and activate a virtual environment:**

    **Recommended (using `uv`):**
    ```bash
    # Create a virtual environment (e.g., in .venv)
    uv venv
    # Activate it
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

    **Alternative (using `venv`):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**

    **Recommended (using `uv`):**
    ```bash
    uv pip install -r requirements.txt
    ```

    **Alternative (using `pip`):**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

To start the MCP server:

```bash
python server.py
```

By default, the server will run on `http://0.0.0.0:7796` using Server-Sent Events (SSE) transport. You should see logging output indicating the server has started and is listening for connections.

Ensure the server is running before starting the client. The client will attempt to connect to the server URL specified within it (defaulting to `http://localhost:7796/sse`).

---

# PokeAPI MCP 伺服器

本專案使用 FastMCP 實作了一個模型上下文協定 (MCP) 伺服器。該伺服器與 [PokeAPI](https://pokeapi.co/) 互動，提供查詢寶可夢 (Pokémon) 和道具資訊的工具。此伺服器旨在方便 AI Agent 使用。

## 主要功能

伺服器提供以下工具：

*   `get_pokemon_details(pokemon_name_or_id: str)`: 獲取特定寶可夢的詳細資訊。
*   `get_pokemon_types(pokemon_name_or_id: str)`: 獲取特定寶可夢的屬性。
*   `get_pokemon_color(pokemon_name_or_id: str)`: 獲取特定寶可夢的圖鑑顏色。
*   `get_pokemon_shape(pokemon_name_or_id: str)`: 獲取特定寶可夢的圖鑑分類外形。
*   `list_all_pokemon_names(limit: int = 2000, offset: int = 0)`: 列出寶可夢的英文名稱，支援分頁。
*   `get_item_details(item_name_or_id: str)`: 獲取特定遊戲內道具的詳細資訊。
*   `list_all_items(limit: int = 100, offset: int = 0)`: 列出遊戲內的道具，支援分頁。

關於每個工具的參數和回傳值的更詳細資訊，請參考 `server.py` 中的 `SERVER_INSTRUCTIONS` 變數和各個工具的 docstrings。

## 設定步驟

1.  **先決條件:**
    *   Python  (建議使用 Python 3.10 或更新版本以獲得 `httpx` 的非同步特性支援)
    *   `uv` (推薦：一個極速的 Python 套件安裝器和解析器。)
    *   或者，如果您不使用 `uv`，則需要 `pip` 和 `virtualenv` (或 `venv`)

2.  **建立並啟用虛擬環境:**

    **推薦 (使用 `uv`):**
    ```bash
    # 建立虛擬環境 (例如在 .venv 資料夾中)
    uv venv
    # 啟用虛擬環境
    source .venv/bin/activate  # Windows 環境: .venv\Scripts\activate
    ```

    **替代方案 (使用 `venv`):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows 環境: venv\Scripts\activate
    ```

3.  **安裝依賴套件:**

    **推薦 (使用 `uv`):**
    ```bash
    uv pip install -r requirements.txt
    ```

    **替代方案 (使用 `pip`):**
    ```bash
    pip install -r requirements.txt
    ```

## 運行伺服器

啟動 MCP 伺服器：

```bash
python server.py
```

預設情況下，伺服器將使用 Server-Sent Events (SSE) 傳輸方式在 `http://0.0.0.0:7796` 上運行。您應該能看到日誌輸出，顯示伺服器已啟動並正在監聽連線。

在啟動客戶端之前，請確保伺服器正在運行。客戶端將嘗試連接到其內部指定的伺服器 URL (預設為 `http://localhost:7796/sse`)。 
