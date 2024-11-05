with open("abbrevations.txt", "r", encoding="utf-8") as file:
    abbrevationsFile = file.read()

abbrevations = abbrevationsFile.split()

with open("example_test.txt", "r", encoding="utf-8") as file:
    text = file.read()

words = text.split()
sentences = []

sentence = ""
inQuotation = False
inParentheses = False
for i, word in enumerate(words):
    sentence = sentence + " " + word

    if (inQuotation == True):
        if word[len(word)-1] == '"':
            inQuotation = False
            if (i+1 < len(words)) and words[i+1][0].isupper():
                sentences.append(sentence)
                sentence = ""
    elif (inParentheses == True):
        if word[len(word)-1] == ')':
            inParentheses = False
            if (i+1 < len(words)) and words[i+1][0].isupper():
                sentences.append(sentence)
                sentence = ""
    else: 
        if word[0] == '"':
            if word[len(word)-1] == '"':
                pass
            else:
                inQuotation = True
        if word[0] == '(':
            if word[len(word)-1] == ')':
                pass
            else:
                inParentheses = True

        if word[len(word)-1] == '.':
            if word in abbrevations:
                pass
            else:
                sentences.append(sentence)
                sentence = ""

        if word[len(word)-1] == '?' or word[len(word)-1] == '!':
            sentences.append(sentence)
            sentence = ""
    
for sentence in sentences:
    print(sentence)