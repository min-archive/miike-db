import sys
import urllib
import json
import argparse
import urllib.request
from rdflib import URIRef, BNode, Literal, Graph
import yaml
import os


def parse_args(args=sys.argv[1:]):
    """ Get the parsed arguments specified on this script.
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'site_name',
        action='store',
        type=str,
        help='Site name. ex: hyakki')

    parser.add_argument(
        'item_set_id',
        action='store',
        type=str,
        help='ID of itemSet. ex: 2')

    return parser.parse_args(args)


def ld_generator(site_name, arg_item_set_id):

    f = open("settings.yml", "r+")
    settings = yaml.load(f)

    api_url = settings["api_url"]

    output_dir = settings["output_dir"] + "/" + site_name + "/metadata"

    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir + "/data.json"

    collection = []

    if arg_item_set_id == "all":
        item_set_arr = [""]
    else :
        item_set_arr = arg_item_set_id.split(",")

    for item_set_id in item_set_arr:

        loop_flg = True
        page = 1

        while loop_flg:
            url = api_url + "/items?item_set_id=" + str(item_set_id) + "&page=" + str(
                page) + "&sort_by=" + settings["sort"] + "&sort_order=asc"
            print(url)

            page += 1

            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)

            response_body = response.read().decode("utf-8")
            data = json.loads(response_body.split('\n')[0])

            if len(data) > 0:
                for i in range(len(data)):
                    collection.append(data[i])

            else:
                loop_flg = False

    fw = open(output_path, 'w')
    json.dump(collection, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

    ld_str = json.dumps(collection)

    g = Graph().parse(data=ld_str, format='json-ld')

    # g.serialize(format='n3', destination=output_path.replace(".json", ".n3"))
    print("converting into nt ...")
    g.serialize(format='nt', destination=output_path.replace(".json", ".nt"))
    print("converting into turtle ...")
    g.serialize(format='turtle', destination=output_path.replace(".json", ".ttl"))
    print("converting into rdf ...")
    g.serialize(format='pretty-xml', destination=output_path.replace(".json", ".rdf"))


if __name__ == "__main__":
    args = parse_args()

    site_name = args.site_name
    arg_item_set_id = args.item_set_id

    ld_generator(site_name, arg_item_set_id)
