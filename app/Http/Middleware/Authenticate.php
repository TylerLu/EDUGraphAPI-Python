<?php

namespace App\Http\Middleware;

use App\Exceptions\ShowException;
use Closure;
use Gate;
use Illuminate\Contracts\Auth\Guard;

class Authenticate
{
    /**
     * The Guard implementation.
     *
     * @var Guard
     */
    protected $auth;

    /**
     * Guard $auth 参数由容器提供,
     * Illuminate\Auth\AuthServiceProvider
     *
     * @param  Guard $auth
     * @return void
     */
    public function __construct(Guard $auth)
    {
        $this->auth = $auth;
    }

    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request $request
     * @param  \Closure                 $next
     * @return mixed
     */
    public function handle($request, Closure $next)
    {
        if ($this->auth->guest()) {
            return redirect()->route('account.login');
        }

        return $next($request);
    }

}
