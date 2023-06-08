using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OnTriggerSetColor : MonoBehaviour
{
    public string targetTag;

    private void OnTriggerEnter(Collider other)
    {
        if(other.tag == targetTag)
        {
            other.GetComponent<MeshRenderer>().material = GetComponent<MeshRenderer>().material;
        }
    }
}
