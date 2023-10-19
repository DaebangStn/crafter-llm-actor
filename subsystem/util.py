def find_word_index(sentence, word_list):
    for i in range(len(sentence)):
        for word in word_list:
            if sentence[i:i+len(word)] == word:
                return word_list.index(word)
    return None
