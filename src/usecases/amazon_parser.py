# import httpx


# class AmazonParser:
#     def __init__(self, urls: list[str]):
#         self.contents = {}
#         for url in urls:
#             response = httpx.get(url)
#             if response.status_code == 200:
#                 self.contents[url] = response.text
#             else:
#                 print(
#                     f"Erreur lors de la récupération de {url}: {response.status_code}"
#                 )

#     def parse(self):
#         # Ici, on simule le parsing en retournant une liste de dictionnaires
#         # représentant les tomes extraits de la page Amazon.
#         # En réalité, vous utiliseriez une bibliothèque comme BeautifulSoup pour faire du vrai parsing HTML.
#         return [
#             {"numero": 1, "titre": "Le Loup Solitaire - Tome 1", "prix": 9.99},
#             {"numero": 2, "titre": "Le Loup Solitaire - Tome 2", "prix": 10.99},
#             {"numero": 3, "titre": "Le Loup Solitaire - Tome 3", "prix": 11.99},
#         ]
