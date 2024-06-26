import os
import argparse

banner='echo ICAgICBfXy9cX18KLiBfICBcXCcnLy8gICAgTXVkZGxlCi0oICktL198fF9cICAgIE1hZ2UKIC4nLiBcXygpXy8KICB8ICAgfCAuIFwgICAKICB8ICAgfCAuICBcICAKIC4nLiAsXF9fX19fJy4gQnk6eDU3Cg== | base64 -d'
os.system(banner)


parser = argparse.ArgumentParser(description='Fuzzing tool in Magento endpoints.')
parser.add_argument('-u', '--url')
parser.add_argument('-w', '--wordlist')
parser.add_argument('-p', '--phpsessid')
parser.add_argument('-o', '--output')
parser.add_argument('-k', '--formkey')
parser.add_argument('-d', '--data', action='store_true')
parser.add_argument('-f', '--form', action='store_true')
parser.add_argument('-F', '--Form', nargs='+', action='append')
args = parser.parse_args()

URL = args.url
OUTPUT = args.output
PHPSESSID = args.phpsessid
FORM_KEY = args.formkey

def escape_special_chars(word):
    special_chars = ['\'', '\"']
    for char in special_chars:
        word = word.replace(char, '\\' + char)
    return word

if args.wordlist:
    with open(args.wordlist, 'r') as f:
        palavras = f.readlines()

if args.phpsessid or args.formkey:
    if args.form:
        headers = {
            'Cookie': f'PHPSESSID={args.phpsessid}',
            #'Cookie': f'form_key={args.form}',
            'Content-Type': 'multipart/form-data',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }

        headers_str = ' '.join(['-H "{}: {}"'.format(key, value) for key, value in headers.items()])

    if args.data:
        headers = {
            'Cookie': f'PHPSESSID={args.phpsessid}',
            #'Cookie': f'form_key={args.form}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }

        headers_str = ' '.join(['-H "{}: {}"'.format(key, value) for key, value in headers.items()])
else:
    print('Use "-p" para fornecer um PHPSESSID válido\nUse "-k" para fornecer um FORM_KEY válido.')
    exit(1)

if args.output or args.url:
    curl_command = None
    if args.data:
        for palavra in palavras:
            fuzz = palavra.strip()
            fuzz = escape_special_chars(fuzz)
            print(f'Fuzz: {fuzz}')


            #curl_command = f'''
#curl {headers_str} -X POST -s -o /dev/null \
    #-w '{{"Status Code": "%{{response_code}}", "Headers Lines": "%{{num_headers}}", "JSON Headers":%{{header_json}}\n}}' \
    #-d 'remove=0&coupon_code={fuzz}&form_key={FORM_KEY}' {URL} > {OUTPUT}'''
            curl_command = f'''
curl {headers_str} -X POST -s -o /dev/null \
-w '{{"Status Code": "%{{response_code}}", "Headers Lines": "%{{num_headers}}", "JSON Headers":%{{header_json}}\n}}' \
-d 'form_key={FORM_KEY}&login%5Busername%5D=078.055.100-16&login%5Bpassword%5D=batata123&login%5Battribute%5D=taxvat&send={fuzz}' {URL} > {OUTPUT}
'''
            
            if curl_command is not None:
                return_json = f'cat {OUTPUT} | jq \'."Status Code",."Headers Lines",.["JSON Headers"]."set-cookie"\''
                decode_json = f'cat {OUTPUT} | jq -r \'.["JSON Headers"]."set-cookie"\' | grep -oP \'mage-messages=\\K[^;]+\' | perl -MURI::Escape -ne \'print uri_unescape($_)\''
                #status_code = f'cat {OUTPUT} | jq -r \'."Status Code"\''
                status_code = f'echo -n $(grep \'Status Code\' {OUTPUT} | cut -d \'"\' -f 4 && echo "\t")'

                #print(curl_command) #Debug curl command
                os.system(curl_command)
                #print(cmd_curl_command)

                cmd_status_code = os.system(status_code)
                #print(cmd_status_code)

                cmd_decode_json = os.system(decode_json)
                #print(cmd_decode_json)
                
            else:
                print('Erro no comando cURL\nVerifique e tente novamente.')


    elif args.form:
        for f in args.Form:

            form_args = ' '.join([f'-F "{form}"' for sublist in args.Form for form in sublist])

            curl_command = f'''
curl {headers_str} -X POST -s -o /dev/null \
-w '{{"Status Code": "%{{response_code}}", "Headers Lines": "%{{num_headers}}", "JSON Headers":%{{header_json}}\n}}' \
-F form_key={FORM_KEY} \
{form_args} \
{URL} > {OUTPUT}
'''

        if curl_command is not None:
            return_json = f'cat {OUTPUT} | jq \'."Status Code",."Headers Lines",.["JSON Headers"]."set-cookie"\''
            decode_json = f'cat {OUTPUT} | jq -r \'.["JSON Headers"]."set-cookie"\' | grep -oP \'mage-messages=\\K[^;]+\' | perl -MURI::Escape -ne \'print uri_unescape($_)\''
            #status_code = f'cat {OUTPUT} | jq -r \'."Status Code"\''
            status_code = f'echo -n $(grep \'Status Code\' {OUTPUT} | cut -d \'"\' -f 4 && echo "\t")'

            #print(curl_command) #Debug curl command
            os.system(curl_command)
            #print(cmd_curl_command)

            cmd_status_code = os.system(status_code)
            #print(cmd_status_code)

            cmd_decode_json = os.system(decode_json)
            #print(cmd_decode_json)
            
        else:
            print('Erro no comando cURL\nVerifique e tente novamente.')
    else:
        print('Use "-u" para forneçer um endpoint. (POST)\nUse "-o" para forneçer um output file.')

print('\n')

