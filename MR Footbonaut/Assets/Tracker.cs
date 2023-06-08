using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class Tracker : MonoBehaviour
{
    string coordFilePath;
    
    void Start()
    {
        coordFilePath = Application.dataPath + "/coordinate.csv";
    }

    void Update()
    {
        Vector3 coord = ReadData(coordFilePath);
        if (coord.z != -1000.0f)
        {
            this.transform.position = coord;
        }
    }

    Vector3 ReadData(string _filePath)
    {
        string[] _data = File.ReadAllText(_filePath).Split(' ');

        float x;
        float y;
        float z;
        try
        {
            x = float.Parse(_data[0]);
            y = float.Parse(_data[1]);
            z = float.Parse(_data[2]);
            return new Vector3(x, y, z);
        }
        catch
        {
            // Debug.Log(e);
            return new Vector3(0.0f, 0.0f, -1000.0f);
        }
        // Debug.Log(_data[0]);
        // Debug.Log(_data[1]);
        // Debug.Log(_data[2]);
        
    }
}
