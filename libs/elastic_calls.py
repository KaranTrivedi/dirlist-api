#!./venv/bin/python

"""
Elasticsearch calls
"""

import base64
import configparser
import sys
import logging
import json
from time import sleep
# import random
# import datetime as DT

from elasticsearch import Elasticsearch, helpers

CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "elastic_calls"

logger = logging.getLogger(__name__)

def elastic_connection(
    host=CONFIG[SECTION]["host"],
    port=CONFIG[SECTION]["port"],
    user=CONFIG[SECTION]["user"],
    password=CONFIG[SECTION]["pass"],
):
    """
    Create and return elastic object

    Args:
        host (int, optional): Server url. Defaults to CONFIG[SECTION]["host"].
        port (str/int, optional): port number. Defaults to CONFIG[SECTION]["port"].
        user (string, optional): username. Defaults to CONFIG[SECTION]["user"].
        password (string, optional): [description]. Defaults to CONFIG[SECTION]["pass"].

    Returns:
        Elasticsearch: returns elasticsearch object.
    """

    passw = base64.b64decode(password).decode("utf-8")

    # if logger.getEffectiveLevel() == 10:
    #    print(passw)

    host = host + ":" + port

    logger.debug(f"{user}, {host}")

    # Create and return elastic object.
    return Elasticsearch([host], http_auth=(user, passw))


def format_index_name(name):
    """
    Use some sensible filters to modify ep names.
    """

    # Lowercase only
    # Cannot include \, /, *, ?, ", <, >, |, space
    # (the character, not the word), ,, #
    # Indices prior to 7.0 could contain a colon (:),
    # but that's been deprecated and won't be supported in 7.0+
    # Cannot start with -, _, +
    # Cannot be . or ..
    # Cannot be longer than 255 characters

    # showname-(episode.lower()), rem ext., rem whtspace, switch "." -> "-"
    return name.lower().replace(" ", "").replace(".", "-").replace(":", "-")


def cluster_health(elastic):
    """
    Check health of cluster.
    """

    while True:
        try:
            status = elastic.cluster.health()["status"]
            logger.info(status)
        except Exception as exp:
            logger.exception(exp)
            return False
        if status in ("yellow", "green"):
            logger.debug(f"Response from elastic: {status}")
            return True

        logger.info(f"Response from elastic: {status}. Checking again in 1s.")
        sleep(1)


def lastdoc(index, type_field, time_field, elastic):
    """
    Search for the timestamp for last document in elastic. If there is no doc, return 0.

    Args:
        index ([type]): [description]
        type_field ([type]): [description]
        time_field ([type]): [description]
        elastic ([type]): [description]

    Returns:
        [type]: [description]
    """

    body = (
        '''
            {
                "_source":
                [
                    "event_time"
                ],
                "query":
                {
                    "match":
                    {
                        "type":"'''
        + type_field
        + """"
                    }
                },
                "sort":
                [{
                    """
        + time_field
        + """:
                    {
                        "order":"desc"
                    }
                }],
                "size": 1
            }
            """
    )

    attempt = 0
    while attempt < 3:
        if cluster_health(elastic=elastic):
            try:
                res = elastic.search(index=index, doc_type="_doc", body=body)
                logger.debug(res)
            except Exception as exp:
                logger.error("search failed.")
                logger.exception(exp)
                return False
                # sys.exit()

            try:
                if not res["_shards"]["failed"]:
                    break
            except Exception as exp:
                logger.error("Malformed reply for search")
                logger.exception(exp)
                return False

        # If something bad return, try again.
        attempt += 1
        sleep(1)

    if attempt == 3:
        return False

    # If total > 0 return count. Other wise return failure:
    if res["hits"]["total"]:
        return res["hits"]["hits"][0]["_source"]["event_time"]
    return 0


# End function

def add_template(template_name, body, elastic, order=0):
    """
    Add template if it doesnt exist.

    Args:
        template_name ([type]): [description]
        body ([type]): [description]
        elastic (Elasticsearch): elasticsearch object
        order (int, optional): Order of template. Defaults to 0.

    Returns:
        (boolean): returns a boolean based on template being added or not.
    """

    # Need to load template with this param.
    # "index_patterns" : ["show-*"],

    try:
        elastic.indices.put_template(name=template_name, body=body, order=order)
        return True

    except Exception as exp:
        logger.exception(exp)
        return False


def gendocs(docs):
    """
    Python generator for creating documents for elastic bulk insert.

    Args:
        docs (list): Send list of dicts with index names

    Yields:
        (iterator): yeilds iterator with formatted docs for ingest.
    """
    for doc in docs:
        # Temp var for ingest
        index = {}
        index["index"] = doc["index"]
        index["_id"] = doc.get("_id")
        doc.pop("index", None)
        doc.pop("_id", None)
        yield {
            "_index": index["index"],
            "_id": index.get("_id"),
            "_source": doc,
        }


def chunks(iterable, batch_length):
    """
    Yield successive n-sized chunks from l.
    Generator is used to split bulk of docs in n number of
    n length lists for ingest to avoid errors from bad documents
    in batches.

    Args:
        iterable (list): Give list of items to be split
        batch_length (int): length of new lists.

    Yields:
        (list): returns list of lists of bactch_length lenght.
    """
    if batch_length > len(iterable):
        yield iterable
    else:
        for i in range(0, len(iterable), batch_length):
            yield iterable[i : i + batch_length]


def elastic_ingest(elastic, docs, chunk_size=int(CONFIG[SECTION]["bulk"])):
    """
    Ingest data into elastic using bulk insert.

    Args:
        elastic (Elasticsearch): Elasticsearch object
        docs ([type]): [description]
        chunk_size ([type], optional): [description]. Defaults to int(CONFIG[SECTION]["bulk"]).
    """

    # This has to be done in batches.. one error will wreck other inserts.
    master = list(chunks(iterable=docs, batch_length=chunk_size))
    for batches in master:
        try:
            # Function call inside function call. Pass list of dictionaries to be ingested.
            # dictionaries will be sliced into bulk length
            logger.debug(helpers.bulk(elastic, gendocs(batches), chunk_size=chunk_size))
        except Exception as exp:
            logger.exception(exp)
        # except (SystemExit, KeyboardInterrupt):
        #     raise
        # except Exception as exception:
        #     logger.error('Exception', exc_info=True)


def search_listed(elastic, search_index, size=10):
    """
    Search full index and return docs as a list.
    Expected inputs: elastic object, index name.
    Optional: Size. returns 10 docs.

    Args:
        elastic (Elasticsearch): Elasticsearch object
        search_index ([type]): [description]
        size (int, optional): [description]. Defaults to 10.

    Returns:
        [type]: [description]
    """

    try:
        results = elastic.search(index=search_index, size=size)
    except Exception as exp:
        logger.exception(exp)
        return None
    # return results
    if "_shards" in results:
        shards = results["_shards"]
        logger.debug(shards)
    if "hits" in results:
        docs = results["hits"]["hits"]

    if (
        shards["failed"] == shards["skipped"] == 0
        and shards["total"] == shards["successful"]
    ):
        return [doc["_source"] for doc in docs]

    logger.error("Something went wrong during search.")
    logger.error(shards)
    return None


def delete_index(elastic, index):
    """
    Delete given index.

    Args:
        elastic (Elasticsearch): Elasticsearch object
        index (string): index name
    """
    try:
        elastic.indices.delete(index=index)
    except Exception as exp:
        logger.exception(exp)


def main():
    """
    Main function
    """
    logging.basicConfig(
        filename=CONFIG[SECTION]["log"],
        level=CONFIG[SECTION]["level"],
        format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    ###########Create connection##################################################
    elastic = elastic_connection()
    ###########Create connection##################################################

    ###########Test connection##################################################

    logger.info(f"Cluster healthy: {cluster_health(elastic=elastic)}")

    ###########Test connection##################################################

    sys.exit()

if __name__ == "__main__":
    main()
