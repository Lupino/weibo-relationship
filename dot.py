import db

def main(dotfile):
    f = open(dotfile, 'w')

    f.write('digraph G {\ngraph [layout=dot rankdir=LR]\n')

    for user in db.get_users():
        f.write('uid_%s[label = "%s"]\n'%(user['uid'], user['nickname']))
        f.flush()

    for relation in db.get_relations():
        f.write('uid_%s -> uid_%s\n'%(relation['fan'], relation['me']))
        f.flush()
    f.write('}\n')
    f.close()

main('myrelation.dot')
