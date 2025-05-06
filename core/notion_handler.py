#Notion handling tools for the agent
import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

notion = None
if NOTION_API_KEY:
    #Connect to the current Notion Integration
    notion = Client(auth=NOTION_API_KEY) 

    #-- Note: Depends on the integration's set up (i.e which pages/databases and their children did we configure to be shared)

    #-- In my case, my Life Wiki (single database for all my daily notes)

    #-- Need to set up another for my blog planner
    
else:
    print("Warning: NOTION_API_KEY not found. Notion functionalities will not be available.")

def list_databases():
    """
    Lists all databases accessible by the integration.
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    try:
        # Search for all databases the integration has access to
        response = notion.search(filter={"property": "object", "value": "database"})
        # Extract relevant information (e.g., database ID and title)
        databases = []
        for db in response.get("results", []):
            db_id = db.get("id")
            title_list = db.get("title", [])
            db_title = title_list[0].get("plain_text", "Untitled Database") if title_list else "Untitled Database"
            databases.append({"id": db_id, "title": db_title})
        return databases
    except Exception as e:
        print(f"Error listing Notion databases: {e}")
        return {"error": str(e), "details": "Failed to list databases."}

def query_database(database_id: str, filter_conditions: dict = None, sort_conditions: list = None):
    """
    Queries a specific database with optional filters and sorts.
    - database_id: The ID of the Notion database.
    - filter_conditions: A dictionary for filtering (Notion API filter object).
    - sort_conditions: A list for sorting (Notion API sort object).
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    try:
        # Ensure that filter_conditions and sort_conditions are None if not provided,
        # as the Notion API expects them to be absent or valid objects.
        query_params = {"database_id": database_id}
        if filter_conditions:
            query_params["filter"] = filter_conditions
        if sort_conditions:
            query_params["sorts"] = sort_conditions

        response = notion.databases.query(**query_params)
        return response  # Returns the raw response which includes pages and other metadata
    except Exception as e:
        print(f"Error querying Notion database {database_id}: {e}")
        return {"error": str(e), "details": f"Failed to query database {database_id}."}

def get_page_content(page_id: str):
    """
    Retrieves the content of a specific page.
    - page_id: The ID of the Notion page.
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    try:
        # Retrieve all blocks (content) for the given page_id
        # This might require pagination if the page content is very long
        all_blocks = []
        start_cursor = None
        while True:
            response = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=start_cursor
            )
            all_blocks.extend(response.get("results", []))
            if not response.get("has_more"):
                break
            start_cursor = response.get("next_cursor")
        return {"page_id": page_id, "blocks": all_blocks}
    except Exception as e:
        print(f"Error retrieving content for Notion page {page_id}: {e}")
        return {"error": str(e), "details": f"Failed to retrieve content for page {page_id}."}

def create_page(parent_db_id: str = None, parent_page_id: str = None, properties: dict = None, children: list = None):
    """
    Creates a new page, either in a database or as a sub-page of another page.
    - parent_db_id: The ID of the parent database (if creating a database entry).
    - parent_page_id: The ID of the parent page (if creating a sub-page).
    - properties: Dictionary of page properties (required for database pages).
    - children: List of block objects for the page content.
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    
    parent_data = {}
    if parent_db_id:
        parent_data = {"database_id": parent_db_id}
    elif parent_page_id:
        parent_data = {"page_id": parent_page_id}
    else:
        return {"error": "Either parent_db_id or parent_page_id must be provided."}

    try:
        create_params = {"parent": parent_data}
        if properties:
            create_params["properties"] = properties
        if children:
            create_params["children"] = children
        
        response = notion.pages.create(**create_params)
        return response # Returns the created page object
    except Exception as e:
        print(f"Error creating Notion page: {e}")
        error_details = f"Failed to create page with parent {parent_data}."
        if hasattr(e, 'body'): # Notion API errors often have a 'body' attribute with more details
            error_details += f" Notion API response: {e.body}"
        return {"error": str(e), "details": error_details}

def update_page(page_id: str, properties: dict = None, children: list = None, archive: bool = None):
    """
    Updates an existing page's properties or content.
    - page_id: The ID of the page to update.
    - properties: Dictionary of page properties to update.
    - children: List of block objects to append or replace. (More complex updates might need block-specific methods)
    - archive: Boolean to archive/unarchive the page.
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    try:
        update_params = {"page_id": page_id}
        if properties is not None:
            update_params["properties"] = properties
        if archive is not None:
            update_params["archived"] = archive
        
        # Note: Updating children (blocks) directly via page update is limited.
        # To add content, use notion.blocks.children.append(block_id=page_id, children=children_blocks)
        # To replace content, one might need to delete existing blocks first.
        # This function currently focuses on property and archive status updates.
        # If 'children' are provided to this function, they are ignored for now.
        
        if children is not None:
            print(f"Warning: 'children' parameter provided to update_page for page {page_id}, "
                  "but this function currently only supports property and archive updates. "
                  "Use dedicated block methods for content changes.")

        if not properties and archive is None:
            return {"warning": "No properties or archive status provided to update.", "page_id": page_id}

        response = notion.pages.update(**update_params)
        return response # Returns the updated page object
    except Exception as e:
        print(f"Error updating Notion page {page_id}: {e}")
        error_details = f"Failed to update page {page_id}."
        if hasattr(e, 'body'):
            error_details += f" Notion API response: {e.body}"
        return {"error": str(e), "details": error_details}

def quick_search_notion(query: str, sort_options: dict = None, filter_options: dict = None):
    """
    Performs a global search across the Notion workspace.
    - query: The search string.
    - sort_options: Optional. Notion API sort object (e.g., {"direction": "ascending", "timestamp": "last_edited_time"}).
    - filter_options: Optional. Notion API filter object (e.g., {"property": "object", "value": "page"}).
                      By default, searches both pages and databases.
    """
    if not notion:
        return {"error": "Notion client not initialized."}
    try:
        search_params = {"query": query}
        if sort_options:
            search_params["sort"] = sort_options
        if filter_options:
            search_params["filter"] = filter_options
        
        response = notion.search(**search_params)
        # We can process the results here to make them more digestible,
        # e.g., extracting titles, URLs, and a snippet of text.
        # For now, returning the raw results.
        return response
    except Exception as e:
        print(f"Error during Notion quick search for query '{query}': {e}")
        error_details = f"Failed to perform quick search for '{query}'."
        if hasattr(e, 'body'):
            error_details += f" Notion API response: {e.body}"
        return {"error": str(e), "details": error_details}

if __name__ == '__main__':
    if notion:
        print("Notion client initialized.")
        print("\nAttempting to list databases...")
        databases_result = list_databases()
        if isinstance(databases_result, list):
            print(f"Found {len(databases_result)} databases:")
            for db in databases_result:
                print(f"  ID: {db['id']}, Title: {db['title']}")

            # Test querying the first database found
            if databases_result:
                first_db_id = databases_result[0]["id"]
                first_db_title = databases_result[0]["title"]
                print(f"\nAttempting to query database: '{first_db_title}' (ID: {first_db_id})...")
                query_result = query_database(database_id=first_db_id)
                if query_result and "results" in query_result:
                    print(f"Successfully queried database. Found {len(query_result['results'])} pages/items.")
                    # Optionally, print some details of the first few items
                    for i, item in enumerate(query_result['results'][:2]): # Print first 2 items
                        print(f"  Item {i+1} ID: {item.get('id')}")
                        # You can extract more properties if needed, e.g., item.get('properties').get('Name').get('title')[0].get('plain_text')

                    # Test getting content of the first page found in the query
                    if query_result.get("results"):
                        first_page_id = query_result["results"][0].get("id")
                        print(f"\nAttempting to get content for page ID: {first_page_id}...")
                        page_content_result = get_page_content(page_id=first_page_id)
                        if page_content_result and "blocks" in page_content_result:
                            print(f"Successfully retrieved content. Found {len(page_content_result['blocks'])} blocks.")
                            # Optionally, print type of first few blocks
                            for i, block in enumerate(page_content_result['blocks'][:3]): # Print first 3 blocks
                                print(f"  Block {i+1} Type: {block.get('type')}")
                        elif page_content_result and "error" in page_content_result:
                            print(f"Error getting page content: {page_content_result['error']}")
                            if "details" in page_content_result:
                                print(f"Details: {page_content_result['details']}")
                        else:
                            print(f"Could not get content for page ID '{first_page_id}' or an unexpected result was returned.")
                    else:
                        print("\nNo pages found in the database query to test get_page_content.")

                    # Test creating a page in the first database
                    print(f"\nAttempting to create a page in database: '{first_db_title}' (ID: {first_db_id})...")
                    try:
                        # First, retrieve the database schema to find the title property name
                        db_schema = notion.databases.retrieve(database_id=first_db_id)
                        title_property_name = None
                        for name, prop in db_schema.get("properties", {}).items():
                            if prop.get("type") == "title":
                                title_property_name = name
                                break
                        
                        if title_property_name:
                            page_properties = {
                                title_property_name: {
                                    "title": [
                                        {
                                            "text": {
                                                "content": "New Test Page from Script"
                                            }
                                        }
                                    ]
                                }
                                # Add other properties here if needed, matching the database schema
                            }
                            page_children = [
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {
                                                "type": "text",
                                                "text": {
                                                    "content": "This is a test page created by the notion_handler.py script."
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                            created_page_result = create_page(
                                parent_db_id=first_db_id,
                                properties=page_properties,
                                children=page_children
                            )
                            if created_page_result and "id" in created_page_result:
                                new_page_id = created_page_result['id']
                                print(f"Successfully created page. ID: {new_page_id}, URL: {created_page_result.get('url')}")

                                # Test updating the created page's title
                                print(f"\nAttempting to update page ID: {new_page_id}...")
                                updated_page_properties = {
                                    title_property_name: {
                                        "title": [
                                            {
                                                "text": {
                                                    "content": "Updated Test Page Title from Script"
                                                }
                                            }
                                        ]
                                    }
                                }
                                updated_page_result = update_page(
                                    page_id=new_page_id,
                                    properties=updated_page_properties
                                )
                                if updated_page_result and "id" in updated_page_result:
                                    print(f"Successfully updated page. ID: {updated_page_result['id']}")
                                    # You could also verify the title by fetching the page again if needed
                                elif updated_page_result and "error" in updated_page_result:
                                    print(f"Error updating page: {updated_page_result['error']}")
                                    if "details" in updated_page_result:
                                        print(f"Details: {updated_page_result['details']}")
                                elif updated_page_result and "warning" in updated_page_result:
                                    print(f"Warning during page update: {updated_page_result['warning']}")
                                else:
                                    print("Could not update page or an unexpected result was returned.")

                            elif created_page_result and "error" in created_page_result:
                                print(f"Error creating page: {created_page_result['error']}")
                                if "details" in created_page_result:
                                    print(f"Details: {created_page_result['details']}")
                            else:
                                print("Could not create page or an unexpected result was returned.")
                        else:
                            print(f"Could not find a 'title' property in database '{first_db_title}'. Skipping page creation test.")
                    except Exception as e_create_test:
                        print(f"Exception during page creation test setup: {e_create_test}")
                
                elif query_result and "error" in query_result:
                    print(f"Error querying database: {query_result['error']}")
                    if "details" in query_result:
                        print(f"Details: {query_result['details']}")
                else:
                    print(f"Could not query database '{first_db_title}' or an unexpected result was returned.")
            
            # Test quick search
            search_query_term = "Huggingface Agents Course" # You might want to use a term you know exists in your Notion
            print("\nAttempting quick search for term: '{search_query_term}'...")
            quick_search_result = quick_search_notion(query=search_query_term)

            if quick_search_result and "results" in quick_search_result:
                print(f"Quick search for '{search_query_term}' found {len(quick_search_result['results'])} items.")
                for i, item in enumerate(quick_search_result['results'][:3]): # Print first 3 items
                    item_title = "Untitled"
                    if item.get("object") == "page":
                        # Try to get page title from properties
                        properties = item.get("properties", {})
                        for prop_name, prop_value in properties.items():
                            if prop_value.get("type") == "title":
                                title_array = prop_value.get("title", [])
                                if title_array and title_array[0].get("plain_text"):
                                    item_title = title_array[0].get("plain_text")
                                    break
                    elif item.get("object") == "database":
                        title_array = item.get("title", [])
                        if title_array and title_array[0].get("plain_text"):
                            item_title = title_array[0].get("plain_text")
                    
                    print(f"  Item {i+1}: Type: {item.get('object')}, ID: {item.get('id')}, Title/Name: {item_title}, URL: {item.get('url', 'N/A')}")
            elif quick_search_result and "error" in quick_search_result:
                print(f"Error during quick search: {quick_search_result['error']}")
                if "details" in quick_search_result:
                    print(f"Details: {quick_search_result['details']}")
            else:
                print(f"Quick search for '{search_query_term}' returned no results or an unexpected error.")

        elif isinstance(databases_result, dict) and "error" in databases_result:
            print(f"Error listing databases: {databases_result['error']}")
            if "details" in databases_result:
                print(f"Details: {databases_result['details']}")
        else:
            print("Could not list databases or an unexpected result was returned.")
    else:
        print("Please set your NOTION_API_KEY in a .env file to run examples.")