try :
    members = ['홍길동', '이순신', '강감찬']

    one = members[5]

    print(one)  # 예외가 발생하지 않을 때 실행할 코드

except Exception as e:
    print("예외가 발생했습니다.", e) # 예외가 발생할 때 실행할 코드

finally:
    print("프로그램 종료")  # 예외가 발생하든 발생하지 않든 실행할 코드

