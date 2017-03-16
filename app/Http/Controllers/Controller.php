<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Bus\DispatchesJobs;
use Illuminate\Routing\Controller as BaseController;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

class Controller extends BaseController
{
    use AuthorizesRequests, DispatchesJobs, ValidatesRequests;

    const AJAX_SUCCESS = 1;

    const AJAX_ERROR = 2;

    public function success($message, $data = [], $return_url = '')
    {


        if (\Request::ajax()) {
            return response()->json(
                [
                    'status' => self::AJAX_SUCCESS,
                    'message'=>$message,
                    'data'=>$data,
                    'return_url' => $return_url
                ]
            );
        } else {
            $script = "<script> alert('$message'); ";
            if (!$return_url && isset($_SERVER['HTTP_REFERER'])) {
                $return_url = $_SERVER['HTTP_REFERER'];
            }
            $script .= $return_url ? "location.href='".$return_url."';</script>" : '</script>';
            return $script;
        }
    }

    /**
     * error
     * @return Response
     * @author hwz
     **/
    public function error($message, $data = [], $return_url = '')
    {
        if (\Request::ajax()) {
            return response()->json(
                [
                    'status' => self::AJAX_ERROR,
                    'message'=>$message,
                    'data'=>$data,
                    'return_url' => $return_url
                ]
            );
        } else {
            $script = "<script> alert('$message'); ";
            if (!$return_url && isset($_SERVER['HTTP_REFERER'])) {
                $return_url = $_SERVER['HTTP_REFERER'];
            }
            $script .= $return_url ? "location.href='".$return_url."';</script>" : '</script>';
            return $script;
        }
    }

    /*
     * json
     * @return
     * @author qy
     * */
    public function json($data, $error=0, $message=0)
    {
        return response()->json(
            [
                'error' => $error,
                'message' => $message,
                'data' => $data,
            ]
        );
    }

    /**
     * 过滤空白字符
     * @return Array
     * @author hwz
     **/
    public function trimAllInput()
    {
        Input::merge(Input::all(), array_map('trim', Input::all()));
        return Input::all();
    }
}
