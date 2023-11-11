import { setRecoil } from "recoil-nexus";
import { TokenService } from "../../clients/auth";
import { OpenAPI as OpenAPIRecording } from "../../clients/recording";
import { OpenAPI as OpenAPIAuth } from "../../clients/auth";
import { OpenAPI as OpenAPIModel } from "../../clients/model";
import { OpenAPI as OpenAPIInference } from "../../clients/inference";
import { authAtom } from "../atoms/apiAtoms";
import { loginPageUIAtom } from "../atoms/UIAtoms";

export default {

    login: async (email: string, password: string, callback = async () => {}) => {
        // try{
            // const ip = "138.68.161.150";
            const ip = "138.68.161.150";
            OpenAPIAuth.BASE = `http://${ip}:8000`;
            OpenAPIRecording.BASE = `http://${ip}:8001`;
            OpenAPIModel.BASE = `http://${ip}:8002`;
            OpenAPIInference.BASE =  `http://${ip}:8006`;
            console.log('Logging in')
            const response = TokenService.getTokenTokenPost({
                username: email,
                password: password,
            });
            const token = (await response).access_token;

            OpenAPIRecording.TOKEN = (token == null) ? '' : token;
            OpenAPIAuth.TOKEN = (token == null) ? '' : token;
            OpenAPIModel.TOKEN = (token == null) ? '' : token;
            OpenAPIInference.TOKEN = (token == null) ? '' : token;
            setRecoil(authAtom, {
                loggedIn: true,
                token: token,
                email: email,
                password: password,
            });
            setRecoil(loginPageUIAtom,
                {
                    incorrectPassword: false,
                }
            );
        // } catch {
        //     setRecoil(loginPageUIAtom,
        //         {
        //             incorrectPassword: true
        //         }
        //     )
        // }
        await callback();
    },

    logout: async () => {
        setRecoil(authAtom, {
            loggedIn: false,
            token: null,
            email: null,
            password: null
        });
        OpenAPIRecording.TOKEN = undefined;
        OpenAPIAuth.TOKEN = undefined;
    }
};
