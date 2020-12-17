#!./venv/bin/python

"""
Elasticsearch calls
"""

import base64
import configparser
import sys
import logging
from time import sleep
# import random
# import datetime as DT

from elasticsearch import Elasticsearch, helpers, client

CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')
SECTION = 'elastic_calls'
logger = logging.getLogger(SECTION)

def elastic_connection(
                    host=CONFIG[SECTION]['host'],\
                    port=CONFIG[SECTION]['port'],\
                    user=CONFIG[SECTION]['user'],\
                    password=CONFIG[SECTION]['pass']):
    '''
    Create and return elastic object
    '''

    passw = base64.b64decode(password).decode("utf-8")

    #if logger.getEffectiveLevel() == 10:
    #    print(passw)

    host = host + ":" + port

    logger.info("%s %s", user, host)

    #Create and return elastic object.
    return Elasticsearch([host], http_auth=(user, passw))

def cluster_health(elastic):

    '''
    Check health of cluster.
    '''

    while True:
        try:
            status = elastic.cluster.health()['status']
            logger.info(status)
        except Exception as exp:
            logger.exception(exp)
            return False
        if status in ("yellow", "green"):
            logger.debug("Response from elastic: %s.", status)
            return True

        logger.info("Response from elastic: %s. Checking again in 1s.", status)
        sleep(1)

def lastdoc(logger, index, type_field, time_field, elastic):
    '''
    Search for the timestamp for last document in elastic. If there is no doc, return 0.
    '''

    body = '''
            {
                "_source":
                [
                    "event_time"
                ],
                "query":
                {
                    "match":
                    {
                        "type":"''' + type_field + '''"
                    }
                },
                "sort":
                [{
                    ''' + time_field + ''':
                    {
                        "order":"desc"
                    }
                }],
                "size": 1
            }
            '''

    attempt = 0
    while attempt < 3:
        if cluster_health(elastic=elastic, logger=logger):
            try:
                res = elastic.search(index=index, doc_type="_doc", body=body)
                logger.debug(res)
            except Exception as exp:
                logger.error("search failed.")
                logger.exception(exp)
                return False
                #sys.exit()

            try:
                if not res['_shards']['failed']:
                    break
            except Exception as exp:
                logger.error("Malformed reply for search")
                logger.exception(exp)
                return False

        #If something bad return, try again.
        attempt += 1
        sleep(1)

    if attempt == 3:
        return False

    #If total > 0 return count. Other wise return failure:
    if res['hits']['total']:
        return res['hits']['hits'][0]['_source']['event_time']
    return 0

#End function

def add_template(logger,\
                    template_name,\
                    body,\
                    elastic,\
                    order=0):
    '''
    Add template if it doesnt exist.
    '''

    try:
        elastic.indices.put_template(name=template_name,\
                                    body=body,\
                                    order=order)
        return True

    except Exception as exp:
        logger.exception(exp)
        return exp

def gendocs(docs):
    '''
    Python generator for creating documents for elastic bulk insert.
    '''
    for doc in docs:
        #Temp var for ingest
        index = {}
        index["index"] = doc["index"]
        index["_id"] = doc.get("_id", None)
        doc.pop('index', None)
        doc.pop('_id', None)
        yield {
            "_index": index["index"],
            "_id": index.get("_id"),
            "_source": doc,
        }

def chunks(iterable, batch_length):
    '''
    Yield successive n-sized chunks from l.
    Generator is used to split bulk of docs in n number of
    n length lists for ingest to avoid errors from bad documents
    in batches.
    '''

    if batch_length > len(iterable):
        yield iterable
    else:
        for i in range(0, len(iterable), batch_length):
            yield iterable[i:i + batch_length]

def elastic_ingest(logger, elastic, docs, chunk_size=int(CONFIG[SECTION]["bulk"])):
    '''
    Ingest data into elastic using bulk insert.
    '''

    #This has to be done in batches.. one error will wreck other inserts.
    master = list(chunks(iterable=docs, batch_length=chunk_size))
    for batches in master:
        try:
            #Function call inside function call. Pass list of dictionaries to be ingested.
            #dictionaries will be sliced into bulk length
            logger.debug(helpers.bulk(elastic, gendocs(batches), chunk_size=chunk_size))
        except Exception as exp:
            logger.exception(exp)

def search_listed(logger, elastic, search_index, size=10):
    '''
    Search full index and return docs as a list.
    Expected inputs: elastic object, index name.
    Optional: Size. returns 10 docs.
    '''

    try:
        results = elastic.search(index=search_index, size=size)
    except Exception as exp:
        logger.exception(exp)
        return None
    #return results
    if "_shards" in results:
        shards = results["_shards"]
        logger.debug(shards)
    if "hits" in results:
        docs = results["hits"]["hits"]

    if shards["failed"] == shards["skipped"] == 0 and shards["total"] == shards["successful"]:
        return [doc["_source"] for doc in docs]

    logger.error("Something went wrong during search.")
    logger.error(shards)
    return None

def delete_index(logger, elastic, index):
    '''
    Delete given index.
    '''

    try:
        elastic.indices.delete(index=index)
    except Exception as exp:
        logger.exception(exp)

def main():
    '''
    Main function
    '''
    logging.basicConfig(filename=CONFIG[SECTION]['log'],\
                        level=CONFIG[SECTION]['level'],\
                        format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',\
                        datefmt='%Y-%m-%d %H:%M:%S')

    ###########Create connection##################################################
    elastic = elastic_connection(logger=logger)
    ###########Create connection##################################################
    ###########Test connection##################################################
    logger.info("Cluster healthy: %s", cluster_health(logger=logger,\
                                                        elastic=elastic))
    ###########Test connection##################################################

    sys.exit()

    ############Function calls##################################################
    #last_timestamp = lastdoc(logger=logger,\
    #                        index="moogjournal",\
    #                        type_field="alerts",\
    #                        time_field="eventt_time",\
    #                        elastic=elastic)
    #if last_timestamp:
    #    logger.info(last_timestamp)
    ###########Function calls##################################################

    ###########Function calls##################################################
    #docs = elastic_calls.search_listed(logger=logger,\
    #                                    search_index=CONFIG[SECTION]['search'],\
    #                                    elastic=elastic)
    #sys.exit()
    ###########Function calls##################################################

    # ###########Test bulk insert.##################################################
    # bulk = []

    # counter = 0
    # #bulk.append(payload)
    # while counter < 9999:
    #     time = 1551229221 + random.randint(-1000000, 1000000)
    #     payload = {
    #         "index" : "moogtest-2019.01",
    #         "type" : "alerts",
    #         "_id" : counter,
    #         "description":"document " + str(counter),
    #         "@timestamp": str(DT.datetime.utcfromtimestamp(time).isoformat())
    #         }
    #     bulk.append(payload)
    #     counter += 1

    # elastic_ingest(logger=logger,\
    #                 elastic=elastic,\
    #                 docs=bulk,\
    #                 chunk_size=int(CONFIG[SECTION]["bulk"]))

    # ###########Test bulk insert.##################################################

    # #add_template(template_name="moogjournal-test", body=TEMPLATE)

if __name__ == "__main__":
    main()
