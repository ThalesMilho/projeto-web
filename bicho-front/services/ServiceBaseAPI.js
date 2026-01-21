import axios from "axios";
import {getCookies, getCookie, setCookies, deleteCookie} from 'cookies-next';

// const BASE_URL = "https://api.salapix.com.br/api";
const BASE_URL = "https://earnest-raisable-overcoldly.ngrok-free.dev/";

const Http = axios.create()
Http.defaults.baseURL = BASE_URL;

export default class ServiceBaseAPI {

    constructor() {
        Http.defaults.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if(getCookie('authToken')) {
            Http.defaults.headers["Authorization"] = "Bearer " + getCookie('authToken')?.trim();
        }
        Http.interceptors.response.use((response) => response, (error) => {
            if(error?.response?.status == 401) {
                const token = getCookie('authToken');
                deleteCookie("authToken");
                // alert("Sessão expirada");
                if(token)
                    window.location.href = "/login";
            }
            return Promise.reject(error);
        });
    }

    getData (res){
        return res.data
    }

    http(){
        return Http
    }

}

