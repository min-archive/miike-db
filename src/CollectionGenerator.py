import sys
import urllib
import json
import argparse
import urllib.request
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


def collection_generator(site_name, arg_item_set_id):
    f = open("settings.yml", "r+")
    settings = yaml.load(f)

    api_url = settings["api_url"]

    output_dir = settings["output_dir"] + "/" + site_name + "/image"

    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir + "/collection.json"

    collection_uri = settings["github_pages_url"] + "/collections/" + site_name + "/image/collection.json"

    collection = dict()
    collection["@context"] = "http://iiif.io/api/presentation/2/context.json"
    collection["@id"] = collection_uri
    collection["@type"] = "sc:Collection"
    manifests = []
    collection["manifests"] = manifests

    if arg_item_set_id == "all":
        item_set_arr = [""]
    else:
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
                    obj = data[i]

                    media_arr = obj["o:media"]

                    if len(media_arr) > 0:

                        id = obj["o:id"]
                        if settings["identifier"] in obj:
                            id = obj[settings["identifier"]][0]["@value"]

                        manifest_uri = api_url.replace("/api", "/iiif") + "/" + str(id) + "/manifest"

                        manifest = dict()
                        manifests.append(manifest)
                        manifest["@id"] = manifest_uri
                        manifest["@type"] = "sc:Manifest"
                        manifest["label"] = obj["dcterms:title"][0]["@value"]

                        if "dcterms:rights" in obj:
                            manifest["license"] = obj["dcterms:rights"][0]["@id"]

            else:
                loop_flg = False

    fw = open(output_path, 'w')
    json.dump(collection, fw, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


if __name__ == "__main__":
    args = parse_args()

    site_name = args.site_name
    arg_item_set_id = args.item_set_id

    collection_generator(site_name, arg_item_set_id)
