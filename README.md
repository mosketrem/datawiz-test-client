Простий джанґо застосунок, що використовує [бібліотеку-клієнт](https://github.com/datawizio/pythonAPI) до REST API [datawiz.io](http://datawiz.io).
Зроблено як тестове завдання для [вакансії](https://datawiz.io/uk/jobs-catalog/back-end-developer/) на сайті [datawiz.io](datawiz.io)
На жаль, реєстрацію нових користувачів з бібліотеки [прибрали](https://github.com/datawizio/pythonAPI/commit/036c64d1199d6e489581259ff6c3cd4870ce503c#diff-789ce4d4d7f3daa6c4344478eebebe00), тому користуватися можна лише ключем та секретом тестового користувача: лоґін - test1@mail.com, секрет
(пароль) - 1qaz.

Застосунок задеплоєно на Heroku: [datawiz-test-client.herokuapp.com](https://datawiz-test-client.herokuapp.com/)

Після першого лоґіну сторінка вантажиться довго, бо довго отримуються дані з datawiz.io. Відтак джанґо кешує сторінку на 15 хвилин, тому вона вантажиться миттєво.
Окрім цього застосунок запам'ятовує, що користувач увійшов. Для цього використовуєтья сесія, яка зберігається в куках (на добу).