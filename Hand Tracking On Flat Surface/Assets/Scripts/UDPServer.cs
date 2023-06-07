using System;
using System.Net;
using System.Net.Sockets;
using System.Globalization;
using System.Text;
using UnityEngine;

public class UDPServer : MonoBehaviour
{
    UdpClient udpClient;
    IPEndPoint remoteEndPoint;

    void Start()
    {
        udpClient = new UdpClient(12345);
        remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
    }

    void Update()
    {
        while (udpClient.Available > 0)
        {
            ReceiveData();
        }
    }

    void ReceiveData()
    {
        byte[] data = udpClient.Receive(ref remoteEndPoint);
        string message = Encoding.UTF8.GetString(data);
        Debug.Log("Received: " + message);

        string[] coords = message.Split(' ');

        if(coords.Length == 3)
        {
            if (float.TryParse(coords[0], NumberStyles.Any, CultureInfo.InvariantCulture, out float x) &&
                float.TryParse(coords[1], NumberStyles.Any, CultureInfo.InvariantCulture, out float y) &&
                float.TryParse(coords[2], NumberStyles.Any, CultureInfo.InvariantCulture, out float z))
            {
                this.transform.localPosition = new Vector3(x, y, z);
                // this.transform.localPosition = new Vector3(x, y, z);
                // this.transform.position = GetComponentByTag<Camera>().InverseTransformPoint(new Vector3(x, y, z));
                // this.transform.position = GameObject.FindGameObjectWithTag("MainCamera").transform.InverseTransformPoint(new Vector3(x, y, z));
                //this.transform.position = GameObject.FindGameObjectWithTag("MainCamera").GetComponent<Camera>().InverseTransformPoint(new Vector3(x, y, z));
            }
        }
    }

    void OnApplicationQuit()
    {
        udpClient.Close();
    }
}
