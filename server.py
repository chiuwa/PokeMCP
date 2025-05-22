from fastmcp import FastMCP
import logging
import httpx # For making HTTP requests to PokeAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = """
Welcome to the PokeAPI MCP Server! 
This server provides tools to query information about Pokémon.

Available Tools Overview:
- `get_pokemon_details`: Get comprehensive details for a specific Pokémon by its English name or Pokedex ID.
- `get_pokemon_types`: Find out the type(s) (e.g., Fire, Water) of a specific Pokémon.
- `get_pokemon_color`: Discover the primary color of a Pokémon (e.g., red, yellow).
- `get_pokemon_shape`: Learn about the physical shape or form of a Pokémon (e.g., humanoid, quadruped).
- `list_all_pokemon_names`: Get a list of all Pokémon names, useful for iteration or broad searches.

Tips for effective use:
- For specific Pokémon, use their English lowercase name (e.g., 'pikachu') or National Pokédex ID (e.g., 25).
- When trying to answer descriptive queries (e.g., 'Find a yellow, bipedal Pokémon'), you might need to combine tools. For instance, first list Pokémon, then get details or specific attributes (color, shape) for each to filter.
- The `list_all_pokemon_names` tool can be a starting point for broader searches if specific names are unknown.
"""

mcp = FastMCP("PokeAPI MCP Server", instructions=SERVER_INSTRUCTIONS) # Standardized server name

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

# This is an internal helper function, NOT an MCP tool
async def fetch_from_pokeapi(endpoint: str) -> dict:
    """Helper function to fetch data from PokeAPI.

    Args:
        endpoint: The API endpoint to call (e.g., /pokemon/pikachu).

    Returns:
        A dictionary containing the JSON response from the API.
        Returns an error dictionary if the request fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{POKEAPI_BASE_URL}{endpoint}")
            response.raise_for_status() # Raises an exception for 4XX/5XX responses
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"PokeAPI request failed: {e.response.status_code} - {e.response.text}")
        return {"error": f"API request failed with status {e.response.status_code}", "details": e.response.text}
    except httpx.RequestError as e:
        logger.error(f"PokeAPI request error: {e}")
        return {"error": "API request error", "details": str(e)}
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching from PokeAPI: {e}")
        return {"error": "An unexpected error occurred", "details": str(e)}

@mcp.tool() # This IS an MCP tool
async def get_pokemon_details(pokemon_name_or_id: str) -> dict:
    """Fetches comprehensive details for a specific Pokémon from PokeAPI.
    Useful when you know the Pokémon's name or ID and need its full profile.

    Args:
        pokemon_name_or_id (str): The English lowercase name (e.g., "pikachu", "charizard") 
                                  or National Pokédex ID (e.g., 25, 6) of the Pokémon.
                                  Example: "pikachu" or 25.

    Returns:
        dict: A dictionary containing key details about the Pokémon:
              - "id" (int): National Pokédex ID.
              - "name" (str): Pokémon's English lowercase name.
              - "height" (int): Height in decimetres.
              - "weight" (int): Weight in hectograms.
              - "types" (list[str]): List of its elemental types (e.g., ["electric"]).
              - "stats" (dict): Dictionary of base stats (e.g., {"hp": 35, "attack": 55, ...}).
              - "sprite_url" (str | None): URL to an official artwork image, if available.
              Returns an error dictionary if the Pokémon is not found or an API error occurs.
              Example error: {"error": "API request failed...", "details": "..."}
    """
    logger.info(f"Tool 'get_pokemon_details' called for: {pokemon_name_or_id}")
    processed_input = str(pokemon_name_or_id).lower()
    data = await fetch_from_pokeapi(f"/pokemon/{processed_input}/")

    if data.get("error"):
        return data # Return the error dict directly

    try:
        types = [t['type']['name'] for t in data.get('types', [])]
        stats = {s['stat']['name']: s['base_stat'] for s in data.get('stats', [])}
        sprite_url = data.get('sprites', {}).get('other', {}).get('official-artwork', {}).get('front_default')
        if not sprite_url:
            sprite_url = data.get('sprites', {}).get('front_default')

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "types": types,
            "stats": stats,
            "sprite_url": sprite_url
        }
    except Exception as e:
        logger.error(f"Error processing Pokémon data for {pokemon_name_or_id}: {e}")
        return {"error": "Failed to process Pokémon data", "details": str(e)}

@mcp.tool()
async def get_pokemon_types(pokemon_name_or_id: str) -> dict:
    """Fetches the elemental types of a specific Pokémon (e.g., Fire, Water, Grass).
    Useful for determining a Pokémon's strengths and weaknesses.

    Args:
        pokemon_name_or_id (str): The English lowercase name (e.g., "bulbasaur") 
                                  or National Pokédex ID (e.g., 1) of the Pokémon.

    Returns:
        dict: A dictionary containing:
              - "name" (str): The Pokémon's name.
              - "id" (int): The Pokémon's ID.
              - "types" (list[str]): A list of its elemental types (e.g., ["grass", "poison"]).
              Returns an error dictionary if not found or on API error.
              Example: {"name": "bulbasaur", "id": 1, "types": ["grass", "poison"]}
    """
    logger.info(f"Tool 'get_pokemon_types' called for: {pokemon_name_or_id}")
    processed_input = str(pokemon_name_or_id).lower()
    data = await fetch_from_pokeapi(f"/pokemon/{processed_input}/")

    if data.get("error"):
        return data

    try:
        types = [t['type']['name'] for t in data.get('types', [])]
        return {"name": data.get("name"), "id": data.get("id"), "types": types}
    except Exception as e:
        logger.error(f"Error processing Pokémon types for {pokemon_name_or_id}: {e}")
        return {"error": "Failed to process Pokémon types", "details": str(e)}

async def get_species_data(pokemon_name_or_id: str) -> dict:
    """Helper to get pokemon-species data, which contains color and shape.
    This is an internal helper, not an MCP tool by itself.
    """
    logger.debug(f"Fetching initial Pokemon data for species for: {pokemon_name_or_id}")
    processed_input = str(pokemon_name_or_id).lower()
    pokemon_data = await fetch_from_pokeapi(f"/pokemon/{processed_input}/")

    if pokemon_data.get("error"):
        return pokemon_data

    species_url = pokemon_data.get('species', {}).get('url')
    if not species_url:
        logger.warning(f"Species URL not found for {pokemon_name_or_id}")
        return {"error": "Species URL not found", "name": pokemon_data.get("name")}
    
    # The species_url is absolute, so we need to remove the base URL part if fetch_from_pokeapi expects a relative path.
    # Or, modify fetch_from_pokeapi to handle absolute URLs, or make a new helper.
    # For now, assuming species_url is full and httpx.AsyncClient can handle it.
    # Let's refine fetch_from_pokeapi or use a direct httpx call for absolute URLs if needed.
    # Quick check: fetch_from_pokeapi prepends POKEAPI_BASE_URL, so it needs a relative path.
    relative_species_endpoint = species_url.replace(POKEAPI_BASE_URL, "")
    
    logger.debug(f"Fetching species data from: {relative_species_endpoint}")
    species_data = await fetch_from_pokeapi(relative_species_endpoint)
    return species_data

@mcp.tool()
async def get_pokemon_color(pokemon_name_or_id: str) -> dict:
    """Fetches the Pokedex color of a specific Pokémon (e.g., red, blue, yellow).
    This information comes from the Pokémon species data.

    Args:
        pokemon_name_or_id (str): The English lowercase name (e.g., "charmander") 
                                  or National Pokédex ID (e.g., 4) of the Pokémon.

    Returns:
        dict: A dictionary containing:
              - "name" (str): The Pokémon's name (or input if species name differs).
              - "id" (int, optional): The Pokémon species ID, if resolvable.
              - "color" (str): The Pokémon's Pokedex color (e.g., "red").
              Returns an error dictionary if not found or on API error.
              Example: {"name": "charmander", "id": 4, "color": "red"}
    """
    logger.info(f"Tool 'get_pokemon_color' called for: {pokemon_name_or_id}")
    data = await get_species_data(pokemon_name_or_id)

    if data.get("error"):
        return data
    
    try:
        color_name = data.get('color', {}).get('name')
        if not color_name:
            return {"error": "Color not found in species data", "name": data.get("name")}
        return {"name": data.get("name", str(pokemon_name_or_id)), "id": data.get("id"), "color": color_name}
    except Exception as e:
        logger.error(f"Error processing Pokémon color for {pokemon_name_or_id}: {e}")
        return {"error": "Failed to process Pokémon color", "details": str(e)}

@mcp.tool()
async def get_pokemon_shape(pokemon_name_or_id: str) -> dict:
    """Fetches the Pokedex shape category of a specific Pokémon (e.g., humanoid, quadruped, wings).
    This information comes from the Pokémon species data.

    Args:
        pokemon_name_or_id (str): The English lowercase name (e.g., "machop") 
                                  or National Pokédex ID (e.g., 66) of the Pokémon.

    Returns:
        dict: A dictionary containing:
              - "name" (str): The Pokémon's name (or input if species name differs).
              - "id" (int, optional): The Pokémon species ID, if resolvable.
              - "shape" (str): The Pokémon's Pokedex shape (e.g., "humanoid").
              Returns an error dictionary if not found or on API error.
              Example: {"name": "machop", "id": 66, "shape": "humanoid"}
    """
    logger.info(f"Tool 'get_pokemon_shape' called for: {pokemon_name_or_id}")
    data = await get_species_data(pokemon_name_or_id)

    if data.get("error"):
        return data

    try:
        shape_name = data.get('shape', {}).get('name')
        if not shape_name:
             return {"error": "Shape not found in species data", "name": data.get("name")}
        return {"name": data.get("name", str(pokemon_name_or_id)), "id": data.get("id"), "shape": shape_name}
    except Exception as e:
        logger.error(f"Error processing Pokémon shape for {pokemon_name_or_id}: {e}")
        return {"error": "Failed to process Pokémon shape", "details": str(e)}

@mcp.tool()
async def list_all_pokemon_names(limit: int = 2000, offset: int = 0) -> dict: # Increased default limit
    """Lists English names of Pokémon, supporting pagination. 
    Useful as a starting point for iterating through Pokémon or for broad searches 
    when the exact name is unknown. The total number of Pokémon can be high.

    Args:
        limit (int, optional): The maximum number of Pokémon names to return. Defaults to 2000.
                               Max value is determined by PokeAPI (around 1300+ as of latest checks).
        offset (int, optional): The offset from which to start listing. Defaults to 0.

    Returns:
        dict: A dictionary containing:
              - "count" (int): The total number of Pokémon resources available in PokeAPI.
              - "pokemon_names" (list[str]): A list of Pokémon English lowercase names.
              Returns an error dictionary on API error.
              Example: {"count": 1302, "pokemon_names": ["bulbasaur", "ivysaur", ...]}
    """
    logger.info(f"Tool 'list_all_pokemon_names' called with limit={limit}, offset={offset}")
    data = await fetch_from_pokeapi(f"/pokemon?limit={limit}&offset={offset}")

    if data.get("error"):
        return data

    try:
        names = [p['name'] for p in data.get('results', [])]
        return {"count": data.get("count"), "pokemon_names": names}
    except Exception as e:
        logger.error(f"Error processing Pokémon list: {e}")
        return {"error": "Failed to process Pokémon list", "details": str(e)}

@mcp.tool()
async def get_item_details(item_name_or_id: str) -> dict:
    """Fetches detailed information about a specific in-game item from PokeAPI.

    Args:
        item_name_or_id (str): The English name (e.g., "poke-ball", "potion") 
                               or ID of the item. Names are case-insensitive.

    Returns:
        dict: A dictionary containing key details about the item:
              - "id" (int): Item ID.
              - "name" (str): Item's English lowercase name.
              - "cost" (int): Cost of the item in Pokédollars (0 if not sold).
              - "category" (str): The category the item belongs to (e.g., "standard-balls").
              - "short_effect" (str): A short description of the item's effect in English.
              - "sprite_url" (str | None): URL to an image of the item, if available.
              Returns an error dictionary if the item is not found or an API error occurs.
    """
    logger.info(f"Tool 'get_item_details' called for: {item_name_or_id}")
    processed_input = str(item_name_or_id).lower()
    # Replace spaces with hyphens for item names like "poke-ball"
    processed_input = processed_input.replace(" ", "-")
    data = await fetch_from_pokeapi(f"/item/{processed_input}/")

    if data.get("error"):
        return data

    try:
        short_effect_english = "N/A"
        for entry in data.get('effect_entries', []):
            if entry.get('language', {}).get('name') == 'en':
                short_effect_english = entry.get('short_effect', 'N/A')
                break
        
        sprite_url = data.get('sprites', {}).get('default')

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "cost": data.get("cost", 0), # Default to 0 if cost is not present
            "category": data.get('category', {}).get('name'),
            "short_effect": short_effect_english,
            "sprite_url": sprite_url
        }
    except Exception as e:
        logger.error(f"Error processing item data for {item_name_or_id}: {e}")
        return {"error": "Failed to process item data", "details": str(e)}

@mcp.tool()
async def list_all_items(limit: int = 100, offset: int = 0) -> dict:
    """Lists in-game items from PokeAPI, supporting pagination.

    Args:
        limit (int, optional): The maximum number of item names to return. Defaults to 100.
        offset (int, optional): The offset from which to start listing. Defaults to 0.

    Returns:
        dict: A dictionary containing:
              - "count" (int): The total number of item resources available.
              - "item_names" (list[str]): A list of item English lowercase names.
              Returns an error dictionary on API error.
    """
    logger.info(f"Tool 'list_all_items' called with limit={limit}, offset={offset}")
    data = await fetch_from_pokeapi(f"/item?limit={limit}&offset={offset}")

    if data.get("error"):
        return data

    try:
        names = [i['name'] for i in data.get('results', [])]
        return {"count": data.get("count"), "item_names": names}
    except Exception as e:
        logger.error(f"Error processing item list: {e}")
        return {"error": "Failed to process item list", "details": str(e)}

if __name__ == '__main__':
    logger.info("Starting MCP server with SSE transport...")
    mcp.run(transport='sse', port=7796, host="0.0.0.0")
    logger.info("MCP server stopped.") 