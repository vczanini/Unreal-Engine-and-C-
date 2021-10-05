"""

inspired by Michael J. Hayford (rayoptics) code

Created by Kai Xin for general text token file processing

goal is to create a general text file reader


"""

import re

# combine continued lines and return it as one line
def next_line(it, line_continue):
    ln = next(it)
    contIndex = ln.rfind(line_continue)
    if contIndex >= 0:
        return ln[:contIndex] + next_line(it,line_continue)
    else:
        return ln
    
# strip inline and whole line comments    
def strip_comments(textLine,comment):
    commentIndex = textLine.find(comment)
    if commentIndex >= 0:
        return textLine[:commentIndex]
    else:
        return textLine

# read file and split it into lines
# remove comments (both new line and inline)
# combine continued lines
# break combined lines (separated by line_end) into lines
def text_to_lines(filename, comment=None, line_continue=None, line_end=None, encoding=None):
    f = open(filename, 'r',encoding=encoding)
    lines = f.read().splitlines()
    # lines=f.readlines()
    # print(lines)
    f.close()
    
    line_out = []
    it = iter(lines)
    while True:
        try:
            if line_continue is not None:
                ln = next_line(it,line_continue)
            else:
                ln = next(it)
            if comment is not None:
                ln = strip_comments(ln, comment)
            if line_end is not None:
                lnList = ln.split(line_end) # break combined lines
            else:
                lnList=[ln]
            for line in lnList:
                line = line.strip()  # strip leading and trailing spaces
                if len(line) > 0:
                        line_out.append(line)

        except StopIteration:
            break

    return line_out


# lines: list of lines
# reg_exp: regular expression used to tokenize the lines
# remove_quote: remove once string quote, either " or '
# return list of tokens in string
def tokenize_lines(lines, reg_exp, remove_quote=True):
    tokens = []    

    for ln in lines:
        tkns = re.findall(reg_exp, ln)
        
        if remove_quote:
            tkns_new=[]
            for t in tkns:
                if t[:1] == '"':
                    tkns_new.append(t.strip('"'))
                elif t[:1] == "'":
                    tkns_new.append(t.strip("'"))
                else:
                    tkns_new.append(t)
            tkns=tkns_new

        tokens.append(tkns)

    
    return tokens




if __name__ == "__main__":

    # code v
    lines=text_to_lines('./ag_triplet.seq',comment='!',line_continue='&',line_end=';')
    keys=tokenize_lines(lines,r"[^'\"\s]\S*|\".+?\"|'.+?'")
    print(keys)


