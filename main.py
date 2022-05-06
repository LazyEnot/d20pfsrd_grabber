from grabbers import feats


def main():
    qeq = feats.grab_feats_other_links(feats.FeatsOther.Animal_Familiar)
    for q in qeq:
        print(q)


if __name__ == "__main__":
    main()
