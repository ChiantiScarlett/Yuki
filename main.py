import fetch

CODE = '005930'  # 삼성전자


def main():
    # fetch.realtime(CODE)
    # fetch.summary(CODE)
    print(fetch.weekly(CODE))


if __name__ == "__main__":
    main()
