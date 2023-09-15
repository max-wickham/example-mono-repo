import { setRecoil } from "recoil-nexus";
import { TokenService } from "../../clients/auth";
import { OpenAPI as OpenAPIRecording } from "../../clients/recording";
import { OpenAPI as OpenAPIAuth } from "../../clients/auth";
import { authAtom } from "../atoms/apiAtoms";
import { loginPageUIAtom } from "../atoms/UIAtoms";


export default {

    login: async (email: string, password: string, callback = async () => {}) => {
        // try{
            OpenAPIAuth.BASE = 'http://localhost:8000';
            OpenAPIRecording.BASE = 'http://localhost:8001';
            console.log('Logging in')
            const response = TokenService.getTokenTokenPost({
                username: email,
                password: password,
            });
            const token = (await response).access_token;

            OpenAPIRecording.TOKEN = (token == null) ? '' : token;
            OpenAPIAuth.TOKEN = (token == null) ? '' : token;
            setRecoil(authAtom, {
                loggedIn: true,
                token: token
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
            token: null
        });
        OpenAPIRecording.TOKEN = undefined;
        OpenAPIAuth.TOKEN = undefined;
    }
};
