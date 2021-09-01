link = "https://www.amazon.com.br/Smart-Monitor-LG-Machine-24TL520S/dp/B07SSCKJJ3/ref=sr_1_7?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=smart+tv&qid=1626360552&sr=8-7"

test_link = link.split('/')[2]
if not (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
    print("Link inválido")

else:
    print("Link válido")