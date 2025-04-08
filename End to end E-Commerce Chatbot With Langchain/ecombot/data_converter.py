import pandas as pd
from langchain_core.documents import Document


def convert_data():
    data_url = "../data/flipkart_product_review.csv"
    dataset = pd.read_csv(data_url)
    # print(dataset.head())

    print(dataset.columns)
    data = dataset[["product_title","review"]]
    # print(data.head())

    product_list = []

    for index, row in data.iterrows():
        obj = {
            'product_title': row['product_title'],
            'review': row['review']
        }

        product_list.append(obj)

    # print(product_list[:5])

    docs = []

    for product in product_list:
        metadata = {"product_title": product["product_title"]}
        doc = Document(page_content= product["review"], metadata= metadata)

        docs.append(doc)

    # print(docs[:5])
    return docs