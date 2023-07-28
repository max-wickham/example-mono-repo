import { setRecoil } from "recoil-nexus";
import { Body_get_token_token_post, TokenService } from "../../client";
import { authAtom } from "../atoms/apiAtoms";
import { loginPageUIAtom } from "../atoms/UIAtoms";



export const authManager = {
    login: async (email: string, password: string, callback = () => {}) => {
        try{
            const response = TokenService.getTokenTokenPost({
                username: email,
                password: password,
            });
            const token = (await response).access_token;
            setRecoil(authAtom, {
                loggedIn: true,
                token: token
            });
            setRecoil(loginPageUIAtom,
                {
                    incorrectPassword: false,
                }
            )
        } catch {
            setRecoil(loginPageUIAtom,
                {
                    incorrectPassword: true
                }
            )
        }
        callback();
    },

    logout: async () => {
        setRecoil(authAtom, {
            loggedIn: false,
            token: null
        });
    }
};
