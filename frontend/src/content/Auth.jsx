import { useLocation, Navigate } from "react-router-dom"
import axios from "axios";

export const removeToken = () => {
    localStorage.removeItem("access_token")
}


export const setToken = (token) => {
    localStorage.setItem("access_token", token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export const fetchToken = () => {
    return localStorage.getItem("access_token")
}

export function RequireToken({children}){
    let auth = fetchToken()
    let location = useLocation()

    if(!auth){

        return <Navigate to="/login" state ={{from : location}}/>;
    }
    return children;
}

