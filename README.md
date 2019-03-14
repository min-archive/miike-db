# みいけ資料館 - データセット

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)  

[みいけ資料館](https://diyhistory.org/miike-db/s/maekawa/)で公開するコレクションのデータセットを公開します。

不定期にデータ更新を行います。

各データセットは以下の要素から構成されます。

<dl>
<dt>画像</dt>
<dd>
画像に関する情報をIIIFコレクション（IIIFマニフェストのリスト）形式で提供します。
</dd>
<dt>メタデータ</dt>
<dd>
コレクション中のアイテムのメタデータの一覧を表形式（MS-Excel, CSV, TSV）とRDF形式（JSON-LD, RDF/XML, Turtle, N-Triples）で提供します。
</dd>
</dl>

* IIIF: [International Image Interoperability Framework](https://iiif.io/)

***

ディレクトリ構造は以下の通りです。

```
docs
│
└───all
|   │
|   └───image
|   │   │   collection.json
|   │
|   └───metadata
|   │   │   data.xlsx
|   │   │   data.csv   
|   │   │   data.tsv  
|   │   │   data.json
|   │   │   data.rdf
|   │   │   data.nt
|   │   │   data.ttl
```
