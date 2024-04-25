def stretch_grade(grade, o_l_sep, o_r_sep, **kwargs):
    # Default values of kwargs
    o_beg = kwargs['o_beg'] if 'o_beg' in kwargs.keys() else 0
    o_end = kwargs['o_end'] if 'o_end' in kwargs.keys() else 11
    n_beg = kwargs['n_beg'] if 'n_beg' in kwargs.keys() else 0
    n_l_sep = kwargs['n_l_sep'] if 'n_l_sep' in kwargs.keys() else o_l_sep
    n_r_sep = kwargs['n_r_sep'] if 'n_r_sep' in kwargs.keys() else 9
    n_end = kwargs['n_end'] if 'n_end' in kwargs.keys() else 10

    #  o — old;  n — new;  l — left;  r — right;  sep — separator;  beg — begin

    #    ───╊╍╍╍╍╍╍╍╍╍╍╍╍╍╋━━━━━━━━╋┅┅┅┅┅┅┅┅┅┅┅┅┅╉───  
    #     o_beg        o_l_sep  o_r_sep         o_end  
    #              
    #                         _
    #                        ┃ ┃
    #                        ┃ ┃
    #                       _┃ ┃_
    #                       ╲   ╱
    #                        ╲_╱
    #
    #   
    #    ───╊╍╍╍╍╍╍╍╋━━━━━━━━━━━━━━━━━━━━╋┅┅┅┅┅┅┅╉───
    #     n_beg  n_l_sep              n_r_sep  n_end

    if o_beg <= grade <= o_l_sep:
        return (grade - o_beg) / (o_l_sep - o_beg) * (n_l_sep - n_beg) + n_beg
    if o_l_sep < grade < o_r_sep:
        return (grade - o_l_sep) / (o_r_sep - o_l_sep) * (n_r_sep - n_l_sep) + n_l_sep
    if o_r_sep <= grade <= o_end:
        return (grade - o_r_sep) / (o_end - o_r_sep) * (n_end - n_r_sep) + n_r_sep
    if grade < o_beg:
        return n_beg
    if o_end < grade:
        return n_end


def calculate_separators(grades, l_cutoff=1 / 30, r_cutoff=1 / 30):
    grades.sort()
    l_separator = grades[int(len(grades) * l_cutoff)]
    r_separator = grades[int(1 - len(grades) * r_cutoff)]
    return (l_separator, r_separator)
