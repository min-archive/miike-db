import sys
import urllib
import json
import argparse
import urllib.request
import csv
import os
import yaml


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


def image_list_generator(site_name, arg_item_set_id):

    f = open("settings.yml", "r+")
    settings = yaml.load(f)

    api_url = settings["api_url"]

    output_dir = settings["output_dir"] + "/" + site_name + "/image"

    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir + "/images.csv"

    f = open(output_path, 'w')
    writer = csv.writer(f, lineterminator='\n')

    writer.writerow(["Media Url", "Item Identifier"])

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
                    obj = data[i]

                    uuid = obj["o:id"]
                    if settings["identifier"] in obj:

                        uuid = obj[settings["identifier"]][0]["@value"]

                    media_arr = obj["o:media"]
                    for media in media_arr:
                        url2 = media["@id"]

                        request2 = urllib.request.Request(url2)
                        response2 = urllib.request.urlopen(request2)

                        response_body2 = response2.read().decode("utf-8")
                        data2 = json.loads(response_body2)

                        source = data2["o:source"]

                        writer.writerow([source, uuid])

            else:
                loop_flg = False

    f.close()


if __name__ == "__main__":
    args = parse_args()

    site_name = args.site_name
    arg_item_set_id = args.item_set_id

    image_list_generator(site_name, arg_item_set_id)
