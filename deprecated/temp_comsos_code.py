def get_transcript_info_from_cosmos(transcript_name: str):
    db_client = get_cosmos_db_client()
    container_client = db_client.get_container_client(TRANSCRIPT_CONTAINER_NAME)
    # QUERY = "SELECT * FROM summaries p WHERE p.transcript_name = @categoryId"
    # CATEGORYID = transcript_name
    # params = [dict(name="@categoryId", value=CATEGORYID)]
    # results = cosmos_container.query_items(
    #     query=QUERY, parameters=params, enable_cross_partition_query=False
    # )
    try:
        result = container_client.read_item(item=transcript_name, partition_key=transcript_name)
        return result
    except:
        return {}
def get_cosmos_db_client():
    cosmos_client = CosmosClient(url=COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db_client = cosmos_client.get_database_client(COSMOS_DATABASE_NAME)
    # container = database.get_container_client(COSMOS_CONTAINER_NAME)
    # database = client.create_database_if_not_exists(id=COSMOS_DATABASE_NAME)
    # key_path = PartitionKey(path="/transcript_name")
    # container = database.create_container_if_not_exists(
    #     id=COSMOS_CONTAINER_NAME, partition_key=key_path, offer_throughput=400
    # )
    return db_client