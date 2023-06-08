using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OriginDefinder : MonoBehaviour
{
    public Transform player;
    bool isSet = false;

    void Start()
    {
        
    }

    void Update()
    {
        if (OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger) && !isSet)
        {
            this.transform.position = player.position;
            this.transform.rotation = player.rotation;
            isSet = true;
        }
    }
}
