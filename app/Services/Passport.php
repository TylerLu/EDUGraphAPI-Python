<?php

namespace App\Services;

use App\Models\AgentShop;
use App\Models\Agent;
use App\Models\Shop;
use App\Models\WechatUser;
use Overtrue\Wechat\Staff;
use Session;
use App\Models\User;
use App\Exceptions\ShowException;
use App\Exceptions\UserNotAuthedException;

/**
 * 通行证类前端用户认证 Passport
 * @author hwz
 */
class Passport
{


    /**
     * 登录
     * @return mixed
     * @author hwz
     **/
    public function attempt($credentials, $type = 'password', $login = true)
    {
        switch ($type) {
            case 'password':
            default:
                $id =  $this->passwordAttempt($credentials);
                break;
        }
        if ($id) {
            if ($login) {
                $this->makeUserLogin($id);
            }
            return true;
        }

        return false;
    }

    /**
     * 退出
     * @return bool
     * @author hwz
     **/
    public function logout()
    {
        return Session::flush();
    }

    /**
     * 检查是否已登录
     *
     * @return bool
     * @author hwz
     **/
    public function check()
    {
        return intval(Session::get($this->getName())) > 0;
    }


    /**
     * 当前登录用户
     * @throws UserNotAuthedException
     * @return User
     * @author hwz
     */
    public function user()
    {
        $user = User::find($this->userId());
        if (!$user) {
            $this->logout();
            throw new UserNotAuthedException("用户不存在");
        }
        return $user;
    }

    /**
     * 设置SESSION
     *
     * @return void
     * @author hwz
     **/
    public function makeUserLogin($id)
    {
        //判断是否代理商
        $user = User::find($id);
        if (!$user) {
            \Log::error("用户ID $id 不存在于用户表中");
            return false;
        }

        $agent = $user->getAgent();
        if ($agent) {
            Session::set('login_agent', $agent);
            //判断是否开通了店铺
            $shop = $agent->shop;
            if ($shop->id) {
                Session::set('login_shop', $shop);
            }
        }
        return Session::set($this->getName(), $id);
    }



    /**
     * 密码登录
     * @param $credentials array 认证信息
     * @return void
     * @author hwz
     **/
    public function passwordAttempt($credentials)
    {
        $user = User::where('phone', '=', $credentials['phone'])->first();

        if ($user && \Hash::check($credentials['password'], $user->password)) {
            return $user->id;
        }
        return false;
    }


    /**
     * Session存储Key名
     * @return string
     * @author hwz
     **/
    public function getName()
    {
        return 'login_client' . md5(get_class($this));
    }

    /**
     * 获得用户ID
     * @throws UserNotAuthedException
     * @return int
     * @author hwz
     */
    public function userId()
    {
        if (!$this->check()) {
            throw new UserNotAuthedException("用户未登录");
        }
        return intval(Session::get($this->getName()));
    }

    /**
     * 密码重置
     * @return void
     * @author hwz
     **/
    public function passwordReset($phone, $old, $new)
    {
        $credentials = [
            'phone'=>$phone,
            'password'=>$old
        ];

        $right = $this->attempt($credentials, 'password', false);

        if ($right) {
            $this->user()->password = $new;
            return $this->user()->save();
        }

        return false;
    }


    /**
     * 手机验证密码重置
     * @return void
     * @author hwz
     **/
    public function passwordResetWithPhoneVerify()
    {

    }
}
