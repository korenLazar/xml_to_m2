import re
from bs4 import BeautifulSoup as bs

QUOT_ENCODING = "&quot;"

XML_FILE_PATH = "Oceania_level_12.xml"

# original_sentences = list()

with open(XML_FILE_PATH, "r") as f:
    content = f.readlines()
    content = "".join(content)
    soup = bs(content, "lxml")
    writings = soup.find_all("writing")
    for i in range(len(writings)):  # TODO: change back to writing in writings?
        if not writings[i].find_all("change"):  # If the writing is not corrected
            continue
        texts = writings[i].find("text").contents
        sentences = writings[i].find_all("sentence")
        # cur_original_sents = list()  # TODO: no need?
        errors_indices, correct_phrases = list(), list()

        cur_token_id, cur_sent_id = 0, 0
        tokens = sentences[cur_sent_id].find_all("token")
        for text in texts:
            is_correction = not isinstance(text, str)
            if is_correction:
                first_token_id = cur_token_id
            phrase = text.find("selection").text.strip() if is_correction else text.strip()

            while phrase:
                if phrase.startswith(tokens[cur_token_id].text):
                    phrase = phrase[len(tokens[cur_token_id].text):].strip()
                    cur_token_id += 1

                elif phrase.startswith(QUOT_ENCODING) and tokens[cur_token_id].text in ['``',
                                                                                        '\'\'']:  # Case of different encoding in the phrase
                    phrase = phrase[len(QUOT_ENCODING):].strip()
                    cur_token_id += 1

                elif tokens[cur_token_id].text.startswith("."):  # Case of ".<word>" token
                    phrase = phrase[len("."):].strip()
                    tokens[cur_token_id].string = tokens[cur_token_id].text[len("."):]

                else:
                    # If tokenization started from the middle of the phrase
                    if tokens[cur_token_id].text in phrase and tokens[cur_token_id + 1].text in phrase:
                        new_index = re.search(rf'\b({tokens[cur_token_id].text})\b', phrase)
                        phrase = phrase[new_index.start():]

                    else:
                        print(
                            f"In writing_id={writings[i].attrs['id']} sentence_id={sentences[cur_sent_id].attrs['id']} "
                            f"token_id={tokens[cur_token_id].attrs['id']}")
                        break  # Move to the next text

                if cur_token_id >= len(tokens):
                    if cur_sent_id + 1 < len(sentences):
                        cur_sent_id += 1
                        tokens, cur_token_id = sentences[cur_sent_id].find_all("token"), 0
            if is_correction:
                # error_symbol = text.find("symbol").text  # TODO: no need?
                correct_phrases.append(text.find("correct").text.strip())
                errors_indices.append((first_token_id + 1, max(first_token_id + 1, cur_token_id)))

        # TODO: delete next two lines?
        # cur_original_sents.append((" ".join([token.text for token in tokens]), int(sentence.attrs["tokencount"])))
        # original_sentences.append(cur_original_sents)
        print(errors_indices)
        print(correct_phrases)
