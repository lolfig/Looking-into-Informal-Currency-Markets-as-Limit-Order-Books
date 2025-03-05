import re

from unidecode import unidecode


def interpret(text):
    # print("="*30)
    # print("Procesando mensajes puros ...")
    p_regex = re.compile(r'.*?([^\s]*?\s*[0-9]*\s*(usd|eur|mlc).*? a \d+)')
    p_regex_groups = re.compile(r'.*?([^\s]*?)\s*([0-9]*)\s*(usd|eur|mlc).*? a (\d+).*')
    text = re.sub(r'([0-9])([^\d])', r'\1 \2', text)
    text = re.sub('\n', ' ', text)
    t = unidecode(text.lower()).replace("$", " usd").replace("dolares", "usd").replace("americanos", "usd").replace(
        "euros", "eur"
    ).replace("  ", " ").replace("  ", " ").replace(" por ", " a ").replace(" x ", " a ").replace(" en ", " a ")
    # print(" working with ",t)
    t = re.sub(r'(?P<name>\d+) mil', '\g<1>000', t)
    t = re.sub(r'mil', '1000', t)
    # print(" working with ",t)
    t = re.sub('tengo', 'vendo', t)
    t = re.sub('necesito', 'compro', t)
    t = re.sub('(\S)*compr(\S)+', 'compro', t)
    t = re.sub('(\S)*vend(\S)+', 'vendo', t)
    # print(" working with ",t)
    m = p_regex.match(t)
    if m:
        output = []
        alguno = False
        offer = ""
        for m in p_regex.split(t):
            m1 = p_regex_groups.match(m)
            if m1:
                # print(m)
                g = list(m1.groups())
                if g[0] == "compro" or g[0] == "vendo":
                    offer = g[0]
                elif offer != "":
                    g[0] = offer
                output += g
                # alguno = True
                # output.append(p_regex_groups.sub(r'\1\2\3 \4',m1.group()).split(" "))
                output.append(m)
        # if not alguno:
        #         print("===============\n esto no dio ",m)
        return output
        # return p_regex.sub(r'\2\3\4 \5',t).split(" ")
    else:
        # print(" not clear ",t)
        return False


