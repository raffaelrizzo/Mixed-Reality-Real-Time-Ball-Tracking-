using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Tracker : MonoBehaviour
{
    string coordFilePath;
    string lockFilePath;
    string[] _data;
    
    void Start()
    {
        coordFilePath = Application.dataPath + "/coordinate.csv";
        lockFilePath = Application.dataPath + "/coordinate.csv.lock";
    }

    void Update()
    {
        Vector3 coord = new Vector3(0.0f, 0.0f, -1000.0f);
        if (!File.Exists(lockFilePath)) // Check if lock file exists
        {
            try
            {
                coord = ReadData(coordFilePath);
            }
            catch (Exception e)
            {
                Debug.Log(e);
            }
        }

        if (coord.z != -1000.0f)
        {
            this.transform.position = coord;
        }
    }

    Vector3 ReadData(string _filePath)
    {
        float x = 0;
        float y = 0;
        float z = -1000.0f;
        try
        {
            _data = File.ReadAllText(_filePath).Split(' ');
            if (_data.Length == 3)
            {
                x = float.Parse(_data[0]);
                y = float.Parse(_data[1]);
                z = float.Parse(_data[2]);
            }
        }
        catch (Exception e)
        {
            Debug.Log(e);
        }
        return new Vector3(x, y, z);
    }
}
