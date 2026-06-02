function setCookie(name, value, days = 7) {

    const date = new Date()

    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))

    const expires = "expires=" + date.toUTCString()

    document.cookie =
        `${encodeURIComponent(name)}=${encodeURIComponent(value)}; ${expires}; path=/`

    console.log('set cookie ' + name)
}

function getCookie(name) {

    const cookieName = encodeURIComponent(name) + "="

    const cookies = document.cookie.split(';')

    for (let cookie of cookies) {

        cookie = cookie.trim()

        if (cookie.indexOf(cookieName) === 0) {

            return decodeURIComponent(
                cookie.substring(cookieName.length)
            )

        }

    }

    return null
}

function deleteCookie(name) {

    document.cookie =
        `${encodeURIComponent(name)}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`

}