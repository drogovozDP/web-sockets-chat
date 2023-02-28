import { useLocation, Navigate } from "react-router-dom"

export const removeToken = () => {
    localStorage.removeItem("access_token")
}

export const setToken = (token) => {
    localStorage.setItem('access_token', token)
}

export const fetchToken = (token) => {
    return localStorage.getItem('access_token')
}

export function RequireToken({children}){
    let auth = fetchToken()
    let location = useLocation()

    if(!auth){

        return <Navigate to='/' state ={{from : location}}/>;
    }
    return children;
}

