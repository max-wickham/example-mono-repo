import React, { memo, useState } from "react";
import { useRecoilValue, useRecoilState } from "recoil";
import { authAtom } from "../models/atoms/apiAtoms";
import {loginPageUIAtom} from "../models/atoms/UIAtoms";
import { StyleSheet, css } from 'aphrodite';

import {
    Button,
    Row,
    Form,
    FormGroup,
    Input,
} from "reactstrap";
import authManager from "../models/managers/authManager";

export const login_page_styles = StyleSheet.create({
    form_styles: {
        display: 'inline-block',
        paddingTop: 100,
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%'
    },
    form_items: {
        clear: 'right',
        width: '20em',
        margin: 'auto',
        marginBottom: 10
    },
    form_button: {
        clear: 'right',
        width: '20em',
        margin: 'auto',
        display: 'inline-block'
    },
    row_style: {
        display: 'flex',
        justifyContent: 'center',
        width: '100%'
    },
    create_new_style: {
        backgroundColor: '#2db4f7',
        boxShadow: 0,
        borderRadius: 10,
        padding: 10,
        paddingRight: 0,
        paddingLeft: 0,
        marginLeft: 25,
        borderColor: '#2db4f7',
        marginTop: 50,
        marginBottom: 20,
        width: '20em'
    },
    invalid_credentials_style: {
        textAlign: 'center',
        clear: 'right',
        width: '20em',
        margin: 'auto',
        display: 'inline-block',
        color: '#e35f5f',
    },
    forget_password: {
        background: 'none !important',
        border: 'none !important',
        textAlign: 'left',
        clear: 'right',
        fontSize: '14px',
        width: '20em',
        margin: '0',
        paddingLeft: '0',
        display: 'inline-block',
        color: '#6c757d !important',
    },
    forget_password_form: {
        display: 'inline-block',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: '100%',
        top: 100,
        position: 'fixed',
        backgroundColor: 'rgb(239, 247, 247)'
    }
});

export const LoginPage = memo(props => {

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const authAtomState = useRecoilValue(authAtom);
    const loginPageUIAtomState = useRecoilValue(loginPageUIAtom);
    const [model, setModel] = useState(false);


    const handleLogin = () => {
        const login_button = document.getElementById("login_button");
        if (login_button) {
            login_button.click();
        }
    }

    const handleEmail = () => {
        const button = document.getElementById("email_button");
        if (button) {
            button.click();
        }
    }

    console.log('Login Page')


    return <>
        <Form className={css(login_page_styles.form_styles)} >
            <FormGroup>
                <Input className={css(login_page_styles.form_items)} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="email"
                    onKeyPress={e => {
                        if (e.key == 'Enter') {
                            handleLogin();
                        }
                    }}></Input>
                <Input className={css(login_page_styles.form_items)} type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="password"
                    onKeyPress={e => {
                        if (e.key == 'Enter') {
                            handleLogin();
                        }
                    }}></Input>
                <Row className={css(login_page_styles.row_style)}>
                    <Button className={css(login_page_styles.forget_password)} onClick={() => setModel(true)}>Forgot Password</Button>
                </Row>
            </FormGroup>
            <Row className={css(login_page_styles.row_style)}>
                {loginPageUIAtomState.incorrectPassword ? <>
                    <p className={css(login_page_styles.invalid_credentials_style)}>Invalid Credentials</p>
                </> : <></>}
            </Row>
            <Row className={css(login_page_styles.row_style)}>
                <Button id="login_button" className={css(login_page_styles.create_new_style)} onClick={() => {
                    // auth_manager.get_auth_key(email, password, () => {
                    //     device_list_manager.get_device_list(); account_manager.get_account_list()
                    // });
                    authManager.login(email, password, () => {

                    });
                }}>Login</Button>
            </Row>
            {model == false ? null :
                <Form className={css(login_page_styles.forget_password_form)} >
                    <FormGroup>
                        <Input className={css(login_page_styles.form_items)} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="email"
                            onKeyPress={e => {
                                if (e.key == 'Enter') {
                                    handleEmail();
                                }
                            }}></Input>
                        <Row className={css(login_page_styles.row_style)}>
                            <Button className={css(login_page_styles.forget_password)} onClick={() => setModel(false)}>Return to login</Button>
                        </Row>
                        <Row id="email_button" className={css(login_page_styles.row_style)}>
                            <Button className={css(login_page_styles.create_new_style)} onClick={() => {
                                // account_manager.send_password_link(email)
                            }}>Send me an email to reset password</Button>
                        </Row>
                    </FormGroup>
                </Form>

            }

        </Form>
    </>
});
