<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Workout;
use Illuminate\Http\Response;

class Api extends Controller {

    public function index() {
        die("howdy");
    }

    public function import() {
        echo "import \r\n";
        $json = json_decode(file_get_contents('php://input'));

        foreach ($json as $num => $workoutData) {
            $workoutData = (array) $workoutData;

            Workout::firstOrCreate([
                'date' => strtotime($workoutData["Date"]),
                'distance' => $workoutData["Distance"],
                'time' => $workoutData["Time"],
                'pace' => $workoutData["Pace"],
                'user' => $workoutData["User"],
            ]);

        }

    }
}