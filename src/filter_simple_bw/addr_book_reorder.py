#!/usr/bin/env python
# -*- coding: utf-8 -*-

def line2lol(lin_in):
    lst_legal = [c for c in ".@abcdefghijklmnopqrstuvwxyzæøå0123456789!#$%&'*+-/=?^_`{|}~"]
    if '@' in lin_in:
        loc_at = lin_in.find('@')
        loc_beg = loc_at
        while loc_beg > 0 and lin_in[loc_beg-1].lower() in lst_legal:
            loc_beg -= 1
        loc_end = loc_at
        while loc_end < len(lin_in) and lin_in[loc_end].lower() in lst_legal:
            loc_end += 1
        str_email = lin_in[loc_beg:loc_end]
        str_head = lin_in[:loc_beg].strip()
        str_tail = lin_in[loc_end:].strip()
        #print "{}|{}|{}".format(str_head, str_email, str_tail).strip('|')
        str_dom = '@'+str_email.split('@')[1]
        return [str_dom, str_email, str_head, str_tail, lin_in.rstrip('\n')]
    else:
        return ['', '', '', '', lin_in]

with open("../filter_simple_bw/personal_black.scaddr") as fil_in:
    lines = fil_in.readlines()
fil_in.close()

lol_lines = list()
for line in lines:
    ##print line.strip()
    lol_lines.append(line2lol(line))
#lol_lines = remove_dupli_from_lol(lol_lines)
lol_lines.sort()  # order by, Domain, email, head, tail,
with open("../filter_simple_bw/personal_black.scaddr", "w") as fil_out:
    fil_out.writelines([tok[4]+'\n' for tok in lol_lines])
fil_in.close()