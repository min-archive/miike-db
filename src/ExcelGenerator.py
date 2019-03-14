import sys
import urllib
import json
import argparse
import urllib.request
import unicodedata
import pandas as pd
import collections
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


def excel_generator(site_name, arg_item_set_id):
    f = open("settings.yml", "r+")
    settings = yaml.load(f)

    label_map = collections.OrderedDict()
    label_map["dcterms:title"] = "タイトル"

    # 共用サーバで利用する独自語彙集
    default_map = collections.OrderedDict()
    for key in settings["metadata"]:
        default_map[key] = settings["metadata"][key]

    # templateで規定されていない語彙集
    etc_map = collections.OrderedDict()

    table = []
    rows = []
    template_arr = []

    api_url = settings["api_url"]

    output_dir = settings["output_dir"] + "/" + site_name + "/metadata"

    os.makedirs(output_dir, exist_ok=True)

    output_path = output_dir + "/data.xlsx"

    loop_flg = True
    page = 1

    is_label = "item_set"

    is_map = {}

    if arg_item_set_id == "all":
        item_set_arr = [""]
    else:
        item_set_arr = arg_item_set_id.split(",")

    # item_set_id毎に実行
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
            data = json.loads(response_body)

            if len(data) > 0:
                for i in range(len(data)):

                    obj = data[i]

                    is_arr = []

                    # テンプレート情報の保存
                    for iset in obj["o:"+is_label]:

                        is_id = iset["@id"]
                        if is_id not in is_map:

                            response2 = urllib.request.urlopen(is_id)
                            response_body2 = response2.read().decode("utf-8")
                            data2 = json.loads(response_body2)

                            label = data2["dcterms:title"][0]["@value"]

                            is_map[is_id] = label

                        is_arr.append(is_map[is_id])

                    obj[is_label] = is_arr

                    # テンプレート情報の保存
                    if obj["o:resource_template"] != None:

                        template_id = obj["o:resource_template"]["@id"]
                        if template_id not in template_arr:
                            template_arr.append(template_id)

                    for key in obj:
                        if not key.startswith("o:") and key != "@type" and key != is_label:
                            if key not in default_map and key not in etc_map and isinstance(obj[key], list):
                                if "property_label" in obj[key][0]:
                                    etc_map[key] = obj[key][0]["property_label"]

                    rows.append(obj)
            else:
                loop_flg = False

    # テンプレート項目の追加
    for template_id in template_arr:
        response = urllib.request.urlopen(template_id)
        response_body = response.read().decode("utf-8")
        data = json.loads(response_body)
        property_arr = data["o:resource_template_property"]
        for property in property_arr:

            property_label = property["o:alternate_label"]

            property_id = property["o:property"]["@id"]

            response = urllib.request.urlopen(property_id)
            response_body = response.read().decode("utf-8")
            data = json.loads(response_body)

            term = data["o:term"]

            if term in etc_map and property_label:
                label_map[term] = property_label

    # 例外語彙の追加
    for key in etc_map:
        if key not in label_map:
            label_map[key] = etc_map[key]

    # 独自語彙の追加
    for key in default_map:
        if key not in label_map:
            label_map[key] = default_map[key]

    # item_setのためのフィールドを用意
    label_map[is_label] = is_label

    # ラベル行
    row1 = []
    table.append(row1)
    # term行
    row2 = []
    table.append(row2)

    for term in label_map:
        if term in label_map:
            row1.append(label_map[term])
            row2.append(term)
        else:
            row1.append(term)
            row2.append(term)

    media_sum = 0

    # 3行目以降
    for obj in rows:
        row = []
        table.append(row)
        for term in label_map:
            text = ""
            if term in obj:

                if term == is_label:
                    is_arr = obj[term]
                    for i in range(len(is_arr)):
                        text += is_arr[i]
                        if i != len(is_arr) - 1:
                            # 複数ある場合にはパイプでつなぐ
                            text += "|"

                else:
                    values = obj[term]
                    for i in range(len(values)):
                        value = values[i]
                        if "@value" in value:
                            text += value["@value"]
                        else:
                            text += value["@id"]
                        if i != len(values) - 1:
                            # 複数ある場合にはパイプでつなぐ
                            text += "|"
            row.append(unicodedata.normalize("NFKC", text))

        media_num = len(obj["o:media"])
        row.append(media_num)
        media_sum += media_num

    row1.append("# of media")
    row2.append(media_sum)

    df = pd.DataFrame(table)

    df.to_excel(output_path, index=False, header=False)
    df.to_csv(output_path.replace("xlsx", "csv"), index=False, header=False)
    df.to_csv(output_path.replace("xlsx", "tsv"), index=False, header=False, sep='\t')


if __name__ == "__main__":
    args = parse_args()

    site_name = args.site_name
    arg_item_set_id = args.item_set_id

    excel_generator(site_name, arg_item_set_id)
